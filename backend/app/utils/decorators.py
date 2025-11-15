"""
데코레이터 유틸리티
인증, 권한 확인 등의 데코레이터
"""
from functools import wraps
from flask import request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models import User
from app.utils.errors import AuthenticationError, AuthorizationError


def jwt_required_custom(fn):
    """
    JWT 토큰 검증 데코레이터 (커스텀 에러 메시지)

    Usage:
        @jwt_required_custom
        def protected_route():
            ...
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except Exception as e:
            raise AuthenticationError('Valid authentication token required')
        return fn(*args, **kwargs)
    return wrapper


def admin_required(fn):
    """
    관리자 권한 필요 데코레이터

    Usage:
        @jwt_required_custom
        @admin_required
        def admin_only_route():
            ...
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            raise AuthenticationError('User not found')

        if not user.is_admin():
            raise AuthorizationError('Admin permission required')

        return fn(*args, **kwargs)
    return wrapper


def editor_required(fn):
    """
    편집자 이상 권한 필요 데코레이터

    Usage:
        @jwt_required_custom
        @editor_required
        def editor_route():
            ...
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            raise AuthenticationError('User not found')

        if not user.is_editor():
            raise AuthorizationError('Editor permission required')

        return fn(*args, **kwargs)
    return wrapper


def get_current_user():
    """
    현재 인증된 사용자 가져오기

    Returns:
        User: 현재 사용자 객체 또는 None
    """
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
        if user_id:
            return User.query.get(user_id)
    except Exception:
        pass
    return None
