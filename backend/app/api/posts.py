"""
Posts API
게시물 관련 엔드포인트
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models import Post, Category, Tag
from app.utils.errors import NotFoundError, ValidationError
from app.utils.decorators import jwt_required_custom, editor_required, get_current_user

posts_bp = Blueprint('posts', __name__)


@posts_bp.route('', methods=['GET'])
def get_posts():
    """
    게시물 목록 조회

    Query Parameters:
        page (int): 페이지 번호 (default: 1)
        per_page (int): 페이지당 개수 (default: 20, max: 100)
        category_id (int): 카테고리 필터
        tag (str): 태그 필터
        published (bool): 발행 상태 필터 (default: true)

    Returns:
        JSON: 게시물 목록
    """
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    category_id = request.args.get('category_id', type=int)
    tag_name = request.args.get('tag', type=str)
    published = request.args.get('published', 'true').lower() == 'true'

    # 기본 쿼리
    query = Post.query

    # 발행 상태 필터
    if published:
        query = query.filter_by(is_published=True)

    # 카테고리 필터
    if category_id:
        query = query.filter_by(category_id=category_id)

    # 태그 필터
    if tag_name:
        tag = Tag.query.filter_by(name=tag_name).first()
        if tag:
            query = query.filter(Post.tags.contains(tag))

    # 정렬 및 페이지네이션
    query = query.order_by(Post.published_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'posts': [post.to_dict(include_content=False) for post in pagination.items],
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev,
        }
    }), 200


@posts_bp.route('/<int:post_id>', methods=['GET'])
def get_post(post_id):
    """
    게시물 상세 조회

    Args:
        post_id: 게시물 ID

    Returns:
        JSON: 게시물 상세 정보
    """
    post = Post.query.get(post_id)

    if not post:
        raise NotFoundError(f'Post with id {post_id} not found')

    # 발행되지 않은 게시물은 관리자만 조회 가능
    if not post.is_published:
        current_user = get_current_user()
        if not current_user or not current_user.is_editor():
            raise NotFoundError('Post not found')

    # 조회수 증가 (발행된 게시물만)
    if post.is_published:
        post.increment_view_count()

    return jsonify(post.to_dict(include_content=True)), 200


@posts_bp.route('/slug/<string:slug>', methods=['GET'])
def get_post_by_slug(slug):
    """
    Slug로 게시물 조회

    Args:
        slug: 게시물 slug

    Returns:
        JSON: 게시물 상세 정보
    """
    post = Post.get_by_slug(slug)

    if not post:
        raise NotFoundError(f'Post with slug "{slug}" not found')

    # 조회수 증가
    post.increment_view_count()

    return jsonify(post.to_dict(include_content=True)), 200


@posts_bp.route('', methods=['POST'])
@jwt_required_custom
@editor_required
def create_post():
    """
    게시물 생성 (편집자 이상)

    Request Body:
        title (str): 제목
        content (str): 내용 (Markdown)
        category_id (int): 카테고리 ID
        tags (list): 태그 이름 리스트
        draft_id (int, optional): 초안 ID
        thumbnail_url (str, optional): 썸네일 URL

    Returns:
        JSON: 생성된 게시물
    """
    data = request.get_json()

    # 필수 필드 검증
    required_fields = ['title', 'content', 'category_id']
    for field in required_fields:
        if field not in data:
            raise ValidationError(f'Missing required field: {field}')

    # 카테고리 존재 확인
    category = Category.query.get(data['category_id'])
    if not category:
        raise ValidationError(f'Category with id {data["category_id"]} not found')

    # 게시물 생성
    from flask_jwt_extended import get_jwt_identity
    user_id = get_jwt_identity()

    post = Post.create(
        user_id=user_id,
        category_id=data['category_id'],
        title=data['title'],
        content=data['content'],
        draft_id=data.get('draft_id'),
        thumbnail_url=data.get('thumbnail_url'),
    )

    # 태그 설정
    if 'tags' in data and isinstance(data['tags'], list):
        post.set_tags(data['tags'])

    # HTML 렌더링
    post.render_content_html()

    db.session.commit()

    return jsonify(post.to_dict(include_content=True)), 201


@posts_bp.route('/<int:post_id>', methods=['PUT'])
@jwt_required_custom
@editor_required
def update_post(post_id):
    """
    게시물 수정 (편집자 이상)

    Args:
        post_id: 게시물 ID

    Request Body:
        title (str, optional): 제목
        content (str, optional): 내용
        category_id (int, optional): 카테고리 ID
        tags (list, optional): 태그 이름 리스트
        thumbnail_url (str, optional): 썸네일 URL

    Returns:
        JSON: 수정된 게시물
    """
    post = Post.query.get(post_id)

    if not post:
        raise NotFoundError(f'Post with id {post_id} not found')

    data = request.get_json()

    # 필드 업데이트
    if 'title' in data:
        post.title = data['title']
        # slug 재생성
        post.slug = Post._generate_unique_slug(data['title'], post.id)

    if 'content' in data:
        post.content = data['content']
        post.render_content_html()

    if 'category_id' in data:
        category = Category.query.get(data['category_id'])
        if not category:
            raise ValidationError(f'Category with id {data["category_id"]} not found')
        post.category_id = data['category_id']

    if 'thumbnail_url' in data:
        post.thumbnail_url = data['thumbnail_url']

    # 태그 업데이트
    if 'tags' in data and isinstance(data['tags'], list):
        post.set_tags(data['tags'])

    db.session.commit()

    return jsonify(post.to_dict(include_content=True)), 200


@posts_bp.route('/<int:post_id>', methods=['DELETE'])
@jwt_required_custom
@editor_required
def delete_post(post_id):
    """
    게시물 삭제 (편집자 이상)

    Args:
        post_id: 게시물 ID

    Returns:
        JSON: 성공 메시지
    """
    post = Post.query.get(post_id)

    if not post:
        raise NotFoundError(f'Post with id {post_id} not found')

    post.delete()

    return jsonify({'message': 'Post deleted successfully'}), 200


@posts_bp.route('/<int:post_id>/publish', methods=['POST'])
@jwt_required_custom
@editor_required
def publish_post(post_id):
    """
    게시물 발행 (편집자 이상)

    Args:
        post_id: 게시물 ID

    Returns:
        JSON: 발행된 게시물
    """
    post = Post.query.get(post_id)

    if not post:
        raise NotFoundError(f'Post with id {post_id} not found')

    if post.is_published:
        raise ValidationError('Post is already published')

    post.publish()

    return jsonify(post.to_dict(include_content=False)), 200


@posts_bp.route('/<int:post_id>/unpublish', methods=['POST'])
@jwt_required_custom
@editor_required
def unpublish_post(post_id):
    """
    게시물 숨기기 (편집자 이상)

    Args:
        post_id: 게시물 ID

    Returns:
        JSON: 숨겨진 게시물
    """
    post = Post.query.get(post_id)

    if not post:
        raise NotFoundError(f'Post with id {post_id} not found')

    if not post.is_published:
        raise ValidationError('Post is not published')

    post.unpublish()

    return jsonify(post.to_dict(include_content=False)), 200
