"""
Draft API

Draft (초안) 관리 엔드포인트:
- CRUD 작업
- 자동 저장
- 발행/예약
- 이미지 첨부
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from pathlib import Path

from app import db
from app.models import Draft, Post, User, Category, WritingStyle
from app.utils.errors import NotFoundError, ValidationError, AuthorizationError
from app.utils.decorators import jwt_required_custom
from app.services.image_processor import ImageProcessor

drafts_bp = Blueprint('drafts', __name__)


@drafts_bp.route('', methods=['GET'])
@jwt_required()
def list_drafts():
    """
    Draft 목록 조회

    Query Parameters:
        - page (int): 페이지 번호 (기본: 1)
        - per_page (int): 페이지당 개수 (기본: 20, 최대: 100)
        - category_id (int): 카테고리 필터 (선택)
        - status (str): 상태 필터 ('draft', 'ai_generated', 선택)
        - user_id (int): 작성자 필터 (선택, Admin/Editor만)

    Returns:
        Draft 목록 및 페이지네이션 정보
    """
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)

    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    category_id = request.args.get('category_id', type=int)
    status = request.args.get('status')
    user_id = request.args.get('user_id', type=int)

    # 쿼리 시작
    query = Draft.query

    # 권한 체크: 일반 사용자는 자신의 Draft만 조회
    if not current_user.is_admin() and current_user.role != 'editor':
        query = query.filter_by(user_id=current_user_id)
    elif user_id:
        # Admin/Editor는 특정 사용자 필터 가능
        query = query.filter_by(user_id=user_id)

    # 필터링
    if category_id:
        query = query.filter_by(category_id=category_id)

    if status:
        if status == 'draft':
            query = query.filter_by(ai_generated=False)
        elif status == 'ai_generated':
            query = query.filter_by(ai_generated=True)

    # 정렬 및 페이지네이션
    pagination = query.order_by(Draft.updated_at.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    return jsonify({
        'drafts': [draft.to_dict() for draft in pagination.items],
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }), 200


@drafts_bp.route('/<int:draft_id>', methods=['GET'])
@jwt_required()
def get_draft(draft_id: int):
    """
    Draft 상세 조회

    Args:
        draft_id: Draft ID

    Returns:
        Draft 상세 정보
    """
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)

    draft = Draft.query.get(draft_id)
    if not draft:
        raise NotFoundError(f'Draft {draft_id} not found')

    # 권한 체크: 작성자 또는 Admin/Editor만 조회 가능
    if draft.user_id != current_user_id:
        if not current_user.is_admin() and current_user.role != 'editor':
            raise AuthorizationError('You can only view your own drafts')

    return jsonify(draft.to_dict()), 200


@drafts_bp.route('', methods=['POST'])
@jwt_required()
def create_draft():
    """
    Draft 생성

    Request Body:
        - title (str, 필수): 제목
        - content (str, 필수): 내용 (마크다운)
        - category_id (int, 필수): 카테고리 ID
        - writing_style_id (int, 선택): 작성 스타일 ID
        - inspiration_id (int, 선택): Inspiration ID

    Returns:
        생성된 Draft
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()

    # Validation
    required_fields = ['title', 'content', 'category_id']
    for field in required_fields:
        if field not in data:
            raise ValidationError(f'Missing required field: {field}')

    title = data['title'].strip()
    content = data['content'].strip()
    category_id = data['category_id']

    if len(title) < 3 or len(title) > 200:
        raise ValidationError('Title must be between 3 and 200 characters')

    if len(content) < 10:
        raise ValidationError('Content must be at least 10 characters')

    # Category 존재 확인
    category = Category.query.get(category_id)
    if not category:
        raise NotFoundError(f'Category {category_id} not found')

    # WritingStyle 확인 (선택)
    writing_style_id = data.get('writing_style_id')
    if writing_style_id:
        style = WritingStyle.query.get(writing_style_id)
        if not style:
            raise NotFoundError(f'WritingStyle {writing_style_id} not found')

    # Draft 생성
    draft = Draft.create(
        user_id=current_user_id,
        category_id=category_id,
        title=title,
        content=content,
        writing_style_id=writing_style_id,
        inspiration_id=data.get('inspiration_id'),
        ai_generated=False
    )

    db.session.commit()

    return jsonify({
        'message': 'Draft created successfully',
        'draft': draft.to_dict()
    }), 201


@drafts_bp.route('/<int:draft_id>', methods=['PUT'])
@jwt_required()
def update_draft(draft_id: int):
    """
    Draft 수정

    Args:
        draft_id: Draft ID

    Request Body:
        - title (str, 선택): 제목
        - content (str, 선택): 내용
        - category_id (int, 선택): 카테고리 ID
        - writing_style_id (int, 선택): 작성 스타일 ID

    Returns:
        수정된 Draft
    """
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)

    draft = Draft.query.get(draft_id)
    if not draft:
        raise NotFoundError(f'Draft {draft_id} not found')

    # 권한 체크
    if draft.user_id != current_user_id:
        if not current_user.is_admin() and current_user.role != 'editor':
            raise AuthorizationError('You can only edit your own drafts')

    # 이미 발행된 경우 수정 불가
    if draft.post_id:
        raise ValidationError('Cannot edit published draft')

    data = request.get_json()

    # 수정
    if 'title' in data:
        title = data['title'].strip()
        if len(title) < 3 or len(title) > 200:
            raise ValidationError('Title must be between 3 and 200 characters')
        draft.title = title

    if 'content' in data:
        content = data['content'].strip()
        if len(content) < 10:
            raise ValidationError('Content must be at least 10 characters')
        draft.content = content

    if 'category_id' in data:
        category = Category.query.get(data['category_id'])
        if not category:
            raise NotFoundError(f'Category {data["category_id"]} not found')
        draft.category_id = data['category_id']

    if 'writing_style_id' in data:
        if data['writing_style_id']:
            style = WritingStyle.query.get(data['writing_style_id'])
            if not style:
                raise NotFoundError(f'WritingStyle {data["writing_style_id"]} not found')
        draft.writing_style_id = data['writing_style_id']

    db.session.commit()

    return jsonify({
        'message': 'Draft updated successfully',
        'draft': draft.to_dict()
    }), 200


@drafts_bp.route('/<int:draft_id>', methods=['DELETE'])
@jwt_required()
def delete_draft(draft_id: int):
    """
    Draft 삭제

    Args:
        draft_id: Draft ID

    Returns:
        성공 메시지
    """
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)

    draft = Draft.query.get(draft_id)
    if not draft:
        raise NotFoundError(f'Draft {draft_id} not found')

    # 권한 체크
    if draft.user_id != current_user_id:
        if not current_user.is_admin():
            raise AuthorizationError('You can only delete your own drafts')

    # 이미 발행된 경우 삭제 불가
    if draft.post_id:
        raise ValidationError('Cannot delete published draft')

    db.session.delete(draft)
    db.session.commit()

    return jsonify({
        'message': 'Draft deleted successfully'
    }), 200


@drafts_bp.route('/<int:draft_id>/publish', methods=['POST'])
@jwt_required()
def publish_draft(draft_id: int):
    """
    Draft 발행

    Args:
        draft_id: Draft ID

    Request Body:
        - scheduled_at (str, 선택): 예약 발행 시간 (ISO 8601)

    Returns:
        생성된 Post
    """
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)

    draft = Draft.query.get(draft_id)
    if not draft:
        raise NotFoundError(f'Draft {draft_id} not found')

    # 권한 체크: Editor 이상
    if current_user.role not in ['editor', 'admin']:
        raise AuthorizationError('Only editors and admins can publish drafts')

    # 작성자 또는 Admin/Editor만 발행 가능
    if draft.user_id != current_user_id:
        if not current_user.is_admin() and current_user.role != 'editor':
            raise AuthorizationError('You can only publish your own drafts')

    # 이미 발행된 경우
    if draft.post_id:
        raise ValidationError('Draft already published')

    data = request.get_json() or {}
    scheduled_at = data.get('scheduled_at')

    # 예약 발행 시간 파싱
    if scheduled_at:
        try:
            scheduled_datetime = datetime.fromisoformat(scheduled_at.replace('Z', '+00:00'))
            if scheduled_datetime <= datetime.utcnow():
                raise ValidationError('Scheduled time must be in the future')
        except ValueError:
            raise ValidationError('Invalid scheduled_at format (use ISO 8601)')
    else:
        scheduled_datetime = None

    # Post 생성
    post = Post.create(
        user_id=draft.user_id,
        category_id=draft.category_id,
        title=draft.title,
        content=draft.content
    )

    # 즉시 발행 또는 예약
    if not scheduled_datetime:
        post.publish()
    # 예약 발행은 향후 구현 (스케줄러에서 처리)

    # Draft와 Post 연결
    draft.post_id = post.id

    db.session.commit()

    return jsonify({
        'message': 'Draft published successfully',
        'post': post.to_dict()
    }), 201


@drafts_bp.route('/<int:draft_id>/autosave', methods=['POST'])
@jwt_required()
def autosave_draft(draft_id: int):
    """
    Draft 자동 저장

    Args:
        draft_id: Draft ID

    Request Body:
        - title (str, 선택): 제목
        - content (str, 선택): 내용

    Returns:
        저장 시간
    """
    current_user_id = get_jwt_identity()

    draft = Draft.query.get(draft_id)
    if not draft:
        raise NotFoundError(f'Draft {draft_id} not found')

    # 권한 체크
    if draft.user_id != current_user_id:
        raise AuthorizationError('You can only autosave your own drafts')

    data = request.get_json()

    # 자동 저장은 검증 없이 저장
    if 'title' in data:
        draft.title = data['title']

    if 'content' in data:
        draft.content = data['content']

    db.session.commit()

    return jsonify({
        'message': 'Draft autosaved',
        'saved_at': draft.updated_at.isoformat()
    }), 200


@drafts_bp.route('/<int:draft_id>/images', methods=['POST'])
@jwt_required()
def upload_draft_image(draft_id: int):
    """
    Draft 이미지 업로드

    Args:
        draft_id: Draft ID

    Request:
        multipart/form-data with 'image' file

    Returns:
        업로드된 이미지 정보
    """
    current_user_id = get_jwt_identity()

    draft = Draft.query.get(draft_id)
    if not draft:
        raise NotFoundError(f'Draft {draft_id} not found')

    # 권한 체크
    if draft.user_id != current_user_id:
        raise AuthorizationError('You can only upload images to your own drafts')

    # 파일 확인
    if 'image' not in request.files:
        raise ValidationError('No image file provided')

    file = request.files['image']
    if file.filename == '':
        raise ValidationError('No selected file')

    try:
        # 이미지 프로세서 초기화
        upload_folder = Path(current_app.config.get('UPLOAD_FOLDER', 'uploads'))
        processor = ImageProcessor(upload_folder)

        # 이미지 업로드 및 처리
        result = processor.upload_image(file, create_thumbnail=True)

        return jsonify({
            'message': 'Image uploaded successfully',
            'image': result
        }), 201

    except ValueError as e:
        raise ValidationError(str(e))
    except Exception as e:
        current_app.logger.error(f'Image upload failed: {str(e)}')
        raise ValidationError('Failed to upload image')


@drafts_bp.route('/<int:draft_id>/images/<filename>', methods=['DELETE'])
@jwt_required()
def delete_draft_image(draft_id: int, filename: str):
    """
    Draft 이미지 삭제

    Args:
        draft_id: Draft ID
        filename: 파일명

    Returns:
        성공 메시지
    """
    current_user_id = get_jwt_identity()

    draft = Draft.query.get(draft_id)
    if not draft:
        raise NotFoundError(f'Draft {draft_id} not found')

    # 권한 체크
    if draft.user_id != current_user_id:
        raise AuthorizationError('You can only delete images from your own drafts')

    try:
        # 이미지 프로세서 초기화
        upload_folder = Path(current_app.config.get('UPLOAD_FOLDER', 'uploads'))
        processor = ImageProcessor(upload_folder)

        # 이미지 삭제
        processor.delete_image(filename, delete_thumbnail=True)

        return jsonify({
            'message': 'Image deleted successfully'
        }), 200

    except Exception as e:
        current_app.logger.error(f'Image deletion failed: {str(e)}')
        raise ValidationError('Failed to delete image')


@drafts_bp.route('/images/<filename>', methods=['GET'])
def get_image_info(filename: str):
    """
    이미지 정보 조회

    Args:
        filename: 파일명

    Returns:
        이미지 정보
    """
    try:
        # 이미지 프로세서 초기화
        upload_folder = Path(current_app.config.get('UPLOAD_FOLDER', 'uploads'))
        processor = ImageProcessor(upload_folder)

        # 이미지 정보 조회
        info = processor.get_image_info(filename)

        if not info:
            raise NotFoundError(f'Image {filename} not found')

        return jsonify(info), 200

    except Exception as e:
        current_app.logger.error(f'Failed to get image info: {str(e)}')
        raise NotFoundError(f'Image {filename} not found')
