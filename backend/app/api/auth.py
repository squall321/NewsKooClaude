"""
Authentication API
JWT 기반 인증 및 사용자 관리
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt
)
from app import db
from app.models import User
from app.utils.errors import ValidationError, AuthenticationError, ConflictError
from app.utils.decorators import admin_required

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
@jwt_required()
@admin_required
def register():
    """
    사용자 등록 (관리자 전용)

    관리자만 새로운 사용자를 생성할 수 있습니다.

    Request Body:
        username (str): 사용자명 (3-50자)
        email (str): 이메일
        password (str): 비밀번호 (최소 8자)
        role (str): 역할 (admin, editor, writer) (default: writer)

    Returns:
        JSON: 생성된 사용자 정보
    """
    data = request.get_json()

    # 필수 필드 검증
    required_fields = ['username', 'email', 'password']
    for field in required_fields:
        if field not in data:
            raise ValidationError(f'Missing required field: {field}')

    # 사용자명 검증
    username = data['username'].strip()
    if len(username) < 3 or len(username) > 50:
        raise ValidationError('Username must be between 3 and 50 characters')

    # 비밀번호 검증
    password = data['password']
    if len(password) < 8:
        raise ValidationError('Password must be at least 8 characters')

    # 이메일 검증 (간단한 검증)
    email = data['email'].strip()
    if '@' not in email:
        raise ValidationError('Invalid email format')

    # 중복 확인
    if User.query.filter_by(username=username).first():
        raise ConflictError(f'Username "{username}" already exists')

    if User.query.filter_by(email=email).first():
        raise ConflictError(f'Email "{email}" already exists')

    # 역할 검증
    role = data.get('role', 'writer')
    if role not in ['admin', 'editor', 'writer']:
        raise ValidationError('Invalid role. Must be admin, editor, or writer')

    # 사용자 생성
    user = User.create(
        username=username,
        email=email,
        password=password,
        role=role
    )

    db.session.commit()

    return jsonify({
        'message': 'User created successfully',
        'user': user.to_dict()
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    로그인

    Request Body:
        username (str): 사용자명
        password (str): 비밀번호

    Returns:
        JSON: Access Token 및 Refresh Token
    """
    data = request.get_json()

    # 필수 필드 검증
    if 'username' not in data or 'password' not in data:
        raise ValidationError('Username and password are required')

    username = data['username']
    password = data['password']

    # 사용자 조회
    user = User.query.filter_by(username=username).first()

    if not user:
        raise AuthenticationError('Invalid username or password')

    # 비밀번호 검증
    if not user.check_password(password):
        raise AuthenticationError('Invalid username or password')

    # 활성 상태 확인
    if not user.is_active:
        raise AuthenticationError('Account is deactivated')

    # JWT 토큰 생성
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict()
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    토큰 갱신

    Refresh Token을 사용하여 새로운 Access Token을 발급합니다.

    Headers:
        Authorization: Bearer <refresh_token>

    Returns:
        JSON: 새로운 Access Token
    """
    current_user_id = get_jwt_identity()

    # 사용자 존재 확인
    user = User.query.get(current_user_id)
    if not user:
        raise AuthenticationError('User not found')

    if not user.is_active:
        raise AuthenticationError('Account is deactivated')

    # 새로운 Access Token 생성
    access_token = create_access_token(identity=current_user_id)

    return jsonify({
        'access_token': access_token
    }), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    현재 사용자 정보 조회

    Headers:
        Authorization: Bearer <access_token>

    Returns:
        JSON: 현재 사용자 정보
    """
    current_user_id = get_jwt_identity()

    user = User.query.get(current_user_id)

    if not user:
        raise AuthenticationError('User not found')

    return jsonify(user.to_dict()), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    로그아웃

    현재는 클라이언트에서 토큰을 삭제하는 방식으로 처리합니다.
    향후 Token Blacklist를 구현할 수 있습니다.

    Headers:
        Authorization: Bearer <access_token>

    Returns:
        JSON: 성공 메시지
    """
    # JWT Token Blacklist는 Phase 후반에 구현 가능
    # 현재는 클라이언트에서 토큰 삭제로 처리

    jti = get_jwt()['jti']  # JWT ID (향후 블랙리스트에 사용 가능)

    return jsonify({
        'message': 'Logout successful'
    }), 200


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """
    비밀번호 변경

    Request Body:
        old_password (str): 현재 비밀번호
        new_password (str): 새 비밀번호 (최소 8자)

    Returns:
        JSON: 성공 메시지
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        raise AuthenticationError('User not found')

    data = request.get_json()

    # 필수 필드 검증
    if 'old_password' not in data or 'new_password' not in data:
        raise ValidationError('Old password and new password are required')

    old_password = data['old_password']
    new_password = data['new_password']

    # 현재 비밀번호 검증
    if not user.check_password(old_password):
        raise AuthenticationError('Current password is incorrect')

    # 새 비밀번호 검증
    if len(new_password) < 8:
        raise ValidationError('New password must be at least 8 characters')

    # 비밀번호 변경
    user.set_password(new_password)
    db.session.commit()

    return jsonify({
        'message': 'Password changed successfully'
    }), 200
