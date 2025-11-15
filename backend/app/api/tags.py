"""
Tags API
태그 관련 엔드포인트
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models import Tag
from app.utils.errors import NotFoundError, ValidationError, ConflictError
from app.utils.decorators import jwt_required_custom, admin_required

tags_bp = Blueprint('tags', __name__)


@tags_bp.route('', methods=['GET'])
def get_tags():
    """
    태그 목록 조회

    Query Parameters:
        sort (str): 정렬 기준 (name, usage_count) (default: name)
        limit (int): 제한 개수 (default: 100)

    Returns:
        JSON: 태그 목록
    """
    sort_by = request.args.get('sort', 'name')
    limit = min(request.args.get('limit', 100, type=int), 500)

    # 정렬
    if sort_by == 'usage_count':
        query = Tag.query.order_by(Tag.usage_count.desc())
    else:
        query = Tag.query.order_by(Tag.name)

    tags = query.limit(limit).all()

    return jsonify({
        'tags': [tag.to_dict() for tag in tags]
    }), 200


@tags_bp.route('/<int:tag_id>', methods=['GET'])
def get_tag(tag_id):
    """
    태그 상세 조회

    Args:
        tag_id: 태그 ID

    Returns:
        JSON: 태그 상세 정보
    """
    tag = Tag.query.get(tag_id)

    if not tag:
        raise NotFoundError(f'Tag with id {tag_id} not found')

    return jsonify(tag.to_dict()), 200


@tags_bp.route('/slug/<string:slug>', methods=['GET'])
def get_tag_by_slug(slug):
    """
    Slug로 태그 조회

    Args:
        slug: 태그 slug

    Returns:
        JSON: 태그 상세 정보
    """
    tag = Tag.query.filter_by(slug=slug).first()

    if not tag:
        raise NotFoundError(f'Tag with slug "{slug}" not found')

    return jsonify(tag.to_dict()), 200


@tags_bp.route('', methods=['POST'])
@jwt_required_custom
@admin_required
def create_tag():
    """
    태그 생성 (관리자 전용)

    Request Body:
        name (str): 태그 이름
        slug (str, optional): URL slug (자동 생성 가능)

    Returns:
        JSON: 생성된 태그
    """
    data = request.get_json()

    # 필수 필드 검증
    if 'name' not in data:
        raise ValidationError('Missing required field: name')

    # 중복 확인
    existing = Tag.query.filter_by(name=data['name']).first()
    if existing:
        raise ConflictError(f'Tag with name "{data["name"]}" already exists')

    # 태그 생성
    tag = Tag.create(
        name=data['name'],
        slug=data.get('slug')  # slug가 없으면 자동 생성
    )

    db.session.commit()

    return jsonify(tag.to_dict()), 201


@tags_bp.route('/<int:tag_id>', methods=['PUT'])
@jwt_required_custom
@admin_required
def update_tag(tag_id):
    """
    태그 수정 (관리자 전용)

    Args:
        tag_id: 태그 ID

    Request Body:
        name (str, optional): 태그 이름
        slug (str, optional): URL slug

    Returns:
        JSON: 수정된 태그
    """
    tag = Tag.query.get(tag_id)

    if not tag:
        raise NotFoundError(f'Tag with id {tag_id} not found')

    data = request.get_json()

    # 이름 변경 시 중복 확인
    if 'name' in data and data['name'] != tag.name:
        existing = Tag.query.filter_by(name=data['name']).first()
        if existing:
            raise ConflictError(f'Tag with name "{data["name"]}" already exists')
        tag.name = data['name']

    if 'slug' in data:
        # slug 중복 확인
        existing = Tag.query.filter_by(slug=data['slug']).first()
        if existing and existing.id != tag_id:
            raise ConflictError(f'Tag with slug "{data["slug"]}" already exists')
        tag.slug = data['slug']

    db.session.commit()

    return jsonify(tag.to_dict()), 200


@tags_bp.route('/<int:tag_id>', methods=['DELETE'])
@jwt_required_custom
@admin_required
def delete_tag(tag_id):
    """
    태그 삭제 (관리자 전용)

    Args:
        tag_id: 태그 ID

    Returns:
        JSON: 성공 메시지
    """
    tag = Tag.query.get(tag_id)

    if not tag:
        raise NotFoundError(f'Tag with id {tag_id} not found')

    tag.delete()

    return jsonify({'message': 'Tag deleted successfully'}), 200
