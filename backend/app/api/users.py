"""
Users API

사용자 관리 엔드포인트:
- 사용자 목록 조회 (Admin)
- 사용자 상세 조회
- 프로필 수정
- 역할 관리 (Admin)
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models import User, Post, Draft
from app.utils.errors import NotFoundError, ValidationError, AuthorizationError
from app.utils.decorators import admin_required

users_bp = Blueprint('users', __name__)


@users_bp.route('', methods=['GET'])
@jwt_required()
@admin_required
def list_users():
    """
    사용자 목록 조회 (Admin만)

    Query Parameters:
        page (int): 페이지 번호
        per_page (int): 페이지당 항목 수
        role (str): 역할 필터
        search (str): 검색어 (username 또는 email)

    Returns:
        사용자 목록
    """
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    role = request.args.get('role')
    search = request.args.get('search')

    query = User.query

    if role:
        query = query.filter(User.role == role)

    if search:
        search_term = f'%{search}%'
        query = query.filter(
            (User.username.like(search_term)) | (User.email.like(search_term))
        )

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    users = []
    for user in pagination.items:
        user_dict = user.to_dict()
        user_dict.pop('password_hash', None)  # 비밀번호 해시 제거
        users.append(user_dict)

    return jsonify({
        'users': users,
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages
        }
    }), 200


@users_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id: int):
    """
    사용자 상세 조회

    Args:
        user_id: 사용자 ID

    Returns:
        사용자 정보 및 통계
    """
    current_user_id = get_jwt_identity()

    user = User.query.get(user_id)
    if not user:
        raise NotFoundError(f'User {user_id} not found')

    # 자신의 정보이거나 Admin인 경우만 조회 가능
    current_user = User.query.get(current_user_id)
    if user_id != current_user_id and current_user.role != 'admin':
        raise AuthorizationError('You can only view your own profile or you must be an admin')

    user_dict = user.to_dict()
    user_dict.pop('password_hash', None)

    # 통계 추가
    post_count = Post.query.filter_by(user_id=user_id).count()
    draft_count = Draft.query.filter_by(user_id=user_id).count()
    published_count = Post.query.filter_by(user_id=user_id, status='published').count()

    user_dict['stats'] = {
        'total_posts': post_count,
        'published_posts': published_count,
        'total_drafts': draft_count
    }

    return jsonify(user_dict), 200


@users_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    현재 로그인한 사용자 정보 조회

    Returns:
        현재 사용자 정보
    """
    current_user_id = get_jwt_identity()
    return get_user(current_user_id)


@users_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_current_user():
    """
    현재 사용자 프로필 수정

    Request:
        {
            "email": str,  # 선택
        }

    Returns:
        수정된 사용자 정보
    """
    current_user_id = get_jwt_identity()

    user = User.query.get(current_user_id)
    if not user:
        raise NotFoundError(f'User {current_user_id} not found')

    data = request.get_json() or {}

    # 이메일 수정
    if 'email' in data:
        email = data['email']
        if email and '@' in email:
            # 이메일 중복 체크
            existing = User.query.filter(
                User.email == email,
                User.id != current_user_id
            ).first()
            if existing:
                raise ValidationError('Email already exists')
            user.email = email

    db.session.commit()

    user_dict = user.to_dict()
    user_dict.pop('password_hash', None)

    return jsonify({
        'message': 'Profile updated successfully',
        'user': user_dict
    }), 200


@users_bp.route('/<int:user_id>/role', methods=['PUT'])
@jwt_required()
@admin_required
def update_user_role(user_id: int):
    """
    사용자 역할 변경 (Admin만)

    Args:
        user_id: 사용자 ID

    Request:
        {
            "role": str  # 'user', 'editor', 'admin'
        }

    Returns:
        수정된 사용자 정보
    """
    user = User.query.get(user_id)
    if not user:
        raise NotFoundError(f'User {user_id} not found')

    data = request.get_json()
    if not data:
        raise ValidationError('Request body is required')

    role = data.get('role')
    valid_roles = ['user', 'editor', 'admin']

    if role not in valid_roles:
        raise ValidationError(f'Role must be one of: {", ".join(valid_roles)}')

    user.role = role
    db.session.commit()

    user_dict = user.to_dict()
    user_dict.pop('password_hash', None)

    return jsonify({
        'message': 'User role updated successfully',
        'user': user_dict
    }), 200


@users_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_user(user_id: int):
    """
    사용자 삭제 (Admin만)

    Args:
        user_id: 사용자 ID

    Returns:
        성공 메시지
    """
    current_user_id = get_jwt_identity()

    # 자기 자신은 삭제할 수 없음
    if user_id == current_user_id:
        raise ValidationError('Cannot delete yourself')

    user = User.query.get(user_id)
    if not user:
        raise NotFoundError(f'User {user_id} not found')

    # 관련 데이터 체크
    post_count = Post.query.filter_by(user_id=user_id).count()
    draft_count = Draft.query.filter_by(user_id=user_id).count()

    if post_count > 0 or draft_count > 0:
        raise ValidationError(f'Cannot delete user with {post_count} posts and {draft_count} drafts')

    db.session.delete(user)
    db.session.commit()

    return jsonify({
        'message': 'User deleted successfully'
    }), 200
