"""
Categories API
카테고리 관련 엔드포인트
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models import Category
from app.utils.errors import NotFoundError, ValidationError, ConflictError
from app.utils.decorators import jwt_required_custom, admin_required

categories_bp = Blueprint('categories', __name__)


@categories_bp.route('', methods=['GET'])
def get_categories():
    """
    카테고리 목록 조회

    Returns:
        JSON: 카테고리 목록
    """
    categories = Category.query.order_by(Category.name).all()

    return jsonify({
        'categories': [category.to_dict() for category in categories]
    }), 200


@categories_bp.route('/<int:category_id>', methods=['GET'])
def get_category(category_id):
    """
    카테고리 상세 조회

    Args:
        category_id: 카테고리 ID

    Returns:
        JSON: 카테고리 상세 정보
    """
    category = Category.query.get(category_id)

    if not category:
        raise NotFoundError(f'Category with id {category_id} not found')

    return jsonify(category.to_dict()), 200


@categories_bp.route('/slug/<string:slug>', methods=['GET'])
def get_category_by_slug(slug):
    """
    Slug로 카테고리 조회

    Args:
        slug: 카테고리 slug

    Returns:
        JSON: 카테고리 상세 정보
    """
    category = Category.query.filter_by(slug=slug).first()

    if not category:
        raise NotFoundError(f'Category with slug "{slug}" not found')

    return jsonify(category.to_dict()), 200


@categories_bp.route('', methods=['POST'])
@jwt_required_custom
@admin_required
def create_category():
    """
    카테고리 생성 (관리자 전용)

    Request Body:
        name (str): 카테고리 이름
        description (str, optional): 설명
        slug (str, optional): URL slug (자동 생성 가능)

    Returns:
        JSON: 생성된 카테고리
    """
    data = request.get_json()

    # 필수 필드 검증
    if 'name' not in data:
        raise ValidationError('Missing required field: name')

    # 중복 확인
    existing = Category.query.filter_by(name=data['name']).first()
    if existing:
        raise ConflictError(f'Category with name "{data["name"]}" already exists')

    # 카테고리 생성
    category = Category.create(
        name=data['name'],
        description=data.get('description'),
        slug=data.get('slug')  # slug가 없으면 자동 생성
    )

    db.session.commit()

    return jsonify(category.to_dict()), 201


@categories_bp.route('/<int:category_id>', methods=['PUT'])
@jwt_required_custom
@admin_required
def update_category(category_id):
    """
    카테고리 수정 (관리자 전용)

    Args:
        category_id: 카테고리 ID

    Request Body:
        name (str, optional): 카테고리 이름
        description (str, optional): 설명
        slug (str, optional): URL slug

    Returns:
        JSON: 수정된 카테고리
    """
    category = Category.query.get(category_id)

    if not category:
        raise NotFoundError(f'Category with id {category_id} not found')

    data = request.get_json()

    # 이름 변경 시 중복 확인
    if 'name' in data and data['name'] != category.name:
        existing = Category.query.filter_by(name=data['name']).first()
        if existing:
            raise ConflictError(f'Category with name "{data["name"]}" already exists')
        category.name = data['name']

    if 'description' in data:
        category.description = data['description']

    if 'slug' in data:
        # slug 중복 확인
        existing = Category.query.filter_by(slug=data['slug']).first()
        if existing and existing.id != category_id:
            raise ConflictError(f'Category with slug "{data["slug"]}" already exists')
        category.slug = data['slug']

    db.session.commit()

    return jsonify(category.to_dict()), 200


@categories_bp.route('/<int:category_id>', methods=['DELETE'])
@jwt_required_custom
@admin_required
def delete_category(category_id):
    """
    카테고리 삭제 (관리자 전용)

    Args:
        category_id: 카테고리 ID

    Returns:
        JSON: 성공 메시지
    """
    category = Category.query.get(category_id)

    if not category:
        raise NotFoundError(f'Category with id {category_id} not found')

    # 카테고리에 게시물이 있는지 확인
    if category.posts.count() > 0:
        raise ValidationError('Cannot delete category with existing posts')

    category.delete()

    return jsonify({'message': 'Category deleted successfully'}), 200
