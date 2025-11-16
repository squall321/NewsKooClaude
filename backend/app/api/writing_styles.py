"""
WritingStyles API

작성 스타일 관리 엔드포인트:
- CRUD 작업
- 사용자별 스타일 관리
- 스타일 템플릿
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models import WritingStyle, User
from app.utils.errors import NotFoundError, ValidationError, AuthorizationError

writing_styles_bp = Blueprint('writing_styles', __name__)


@writing_styles_bp.route('', methods=['GET'])
@jwt_required()
def list_writing_styles():
    """WritingStyle 목록 조회"""
    current_user_id = get_jwt_identity()

    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)

    # 현재 사용자의 스타일만 조회
    query = WritingStyle.query.filter_by(user_id=current_user_id)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    styles = [style.to_dict() for style in pagination.items]

    return jsonify({
        'writing_styles': styles,
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages
        }
    }), 200


@writing_styles_bp.route('/<int:style_id>', methods=['GET'])
@jwt_required()
def get_writing_style(style_id: int):
    """WritingStyle 상세 조회"""
    current_user_id = get_jwt_identity()

    style = WritingStyle.query.get(style_id)
    if not style:
        raise NotFoundError(f'WritingStyle {style_id} not found')

    if style.user_id != current_user_id:
        raise AuthorizationError('You can only view your own writing styles')

    return jsonify(style.to_dict()), 200


@writing_styles_bp.route('', methods=['POST'])
@jwt_required()
def create_writing_style():
    """WritingStyle 생성"""
    current_user_id = get_jwt_identity()

    data = request.get_json()
    if not data:
        raise ValidationError('Request body is required')

    name = data.get('name')
    if not name or len(name.strip()) < 2:
        raise ValidationError('Name must be at least 2 characters')

    description = data.get('description', '')
    tone = data.get('tone', 'neutral')
    style_guide = data.get('style_guide', '')

    style = WritingStyle.create(
        user_id=current_user_id,
        name=name.strip(),
        description=description,
        tone=tone,
        style_guide=style_guide
    )

    return jsonify({
        'message': 'WritingStyle created successfully',
        'writing_style': style.to_dict()
    }), 201


@writing_styles_bp.route('/<int:style_id>', methods=['PUT'])
@jwt_required()
def update_writing_style(style_id: int):
    """WritingStyle 수정"""
    current_user_id = get_jwt_identity()

    style = WritingStyle.query.get(style_id)
    if not style:
        raise NotFoundError(f'WritingStyle {style_id} not found')

    if style.user_id != current_user_id:
        raise AuthorizationError('You can only update your own writing styles')

    data = request.get_json() or {}

    if 'name' in data:
        name = data['name']
        if len(name.strip()) >= 2:
            style.name = name.strip()

    if 'description' in data:
        style.description = data['description']

    if 'tone' in data:
        style.tone = data['tone']

    if 'style_guide' in data:
        style.style_guide = data['style_guide']

    db.session.commit()

    return jsonify({
        'message': 'WritingStyle updated successfully',
        'writing_style': style.to_dict()
    }), 200


@writing_styles_bp.route('/<int:style_id>', methods=['DELETE'])
@jwt_required()
def delete_writing_style(style_id: int):
    """WritingStyle 삭제"""
    current_user_id = get_jwt_identity()

    style = WritingStyle.query.get(style_id)
    if not style:
        raise NotFoundError(f'WritingStyle {style_id} not found')

    if style.user_id != current_user_id:
        raise AuthorizationError('You can only delete your own writing styles')

    db.session.delete(style)
    db.session.commit()

    return jsonify({
        'message': 'WritingStyle deleted successfully'
    }), 200
