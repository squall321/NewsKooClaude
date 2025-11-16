"""
Inspiration API

영감(Inspiration) 관리 엔드포인트:
- CRUD 작업
- 필터링 및 검색
- Draft 생성 연동
- 승인/거부 워크플로우
- 통계 조회
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from app import db
from app.models import Inspiration, Source, Draft, User, Category, WritingStyle
from app.services.content_generator import ContentGenerator
from app.utils.errors import NotFoundError, ValidationError, AuthorizationError
from app.utils.decorators import jwt_required_custom, admin_required, editor_required

inspirations_bp = Blueprint('inspirations', __name__)


@inspirations_bp.route('', methods=['GET'])
@jwt_required()
def list_inspirations():
    """
    Inspiration 목록 조회

    Query Parameters:
        page (int): 페이지 번호 (기본: 1)
        per_page (int): 페이지당 항목 수 (기본: 20, 최대: 100)
        status (str): 상태 필터 ('pending', 'approved', 'rejected', 'used')
        min_similarity (float): 최소 유사도 (0.0-1.0)
        max_similarity (float): 최대 유사도 (0.0-1.0)
        source_platform (str): 소스 플랫폼 ('reddit' 등)
        has_draft (bool): Draft 존재 여부
        sort_by (str): 정렬 기준 ('created_at', 'similarity_score', 'source_upvotes')
        order (str): 정렬 순서 ('asc', 'desc')

    Returns:
        {
            "inspirations": [...],
            "pagination": {...}
        }
    """
    current_user_id = get_jwt_identity()

    # 페이지네이션
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)

    # 필터링
    status = request.args.get('status')
    min_similarity = request.args.get('min_similarity', type=float)
    max_similarity = request.args.get('max_similarity', type=float)
    source_platform = request.args.get('source_platform')
    has_draft = request.args.get('has_draft', type=lambda v: v.lower() == 'true' if v else None)

    # 정렬
    sort_by = request.args.get('sort_by', 'created_at')
    order = request.args.get('order', 'desc')

    # 쿼리 생성
    query = Inspiration.query

    # 필터 적용
    if status:
        query = query.filter(Inspiration.status == status)

    if min_similarity is not None:
        query = query.filter(Inspiration.similarity_score >= min_similarity)

    if max_similarity is not None:
        query = query.filter(Inspiration.similarity_score <= max_similarity)

    if source_platform:
        query = query.join(Source).filter(Source.platform == source_platform)

    if has_draft is not None:
        if has_draft:
            query = query.filter(Inspiration.draft_id.isnot(None))
        else:
            query = query.filter(Inspiration.draft_id.is_(None))

    # 정렬 적용
    if sort_by == 'created_at':
        sort_column = Inspiration.created_at
    elif sort_by == 'similarity_score':
        sort_column = Inspiration.similarity_score
    elif sort_by == 'source_upvotes':
        query = query.join(Source)
        sort_column = Source.upvotes
    else:
        sort_column = Inspiration.created_at

    if order == 'desc':
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # 페이지네이션 실행
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    # 응답 생성
    inspirations = []
    for inspiration in pagination.items:
        inspirations.append(inspiration.to_dict())

    return jsonify({
        'inspirations': inspirations,
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }), 200


@inspirations_bp.route('/<int:inspiration_id>', methods=['GET'])
@jwt_required()
def get_inspiration(inspiration_id: int):
    """
    Inspiration 상세 조회

    Args:
        inspiration_id: Inspiration ID

    Returns:
        Inspiration 객체
    """
    current_user_id = get_jwt_identity()

    inspiration = Inspiration.query.get(inspiration_id)
    if not inspiration:
        raise NotFoundError(f'Inspiration {inspiration_id} not found')

    return jsonify(inspiration.to_dict()), 200


@inspirations_bp.route('/<int:inspiration_id>', methods=['PUT'])
@jwt_required()
@editor_required
def update_inspiration(inspiration_id: int):
    """
    Inspiration 수정 (Editor 이상)

    Args:
        inspiration_id: Inspiration ID

    Request:
        {
            "concept": str,           # 컨셉 (선택)
            "notes": str,            # 메모 (선택)
            "status": str            # 상태 (선택: pending, approved, rejected)
        }

    Returns:
        수정된 Inspiration 객체
    """
    current_user_id = get_jwt_identity()

    inspiration = Inspiration.query.get(inspiration_id)
    if not inspiration:
        raise NotFoundError(f'Inspiration {inspiration_id} not found')

    data = request.get_json() or {}

    # 컨셉 수정
    if 'concept' in data:
        concept = data['concept']
        if concept and len(concept.strip()) >= 10:
            inspiration.concept = concept.strip()

    # 메모 수정
    if 'notes' in data:
        inspiration.notes = data['notes']

    # 상태 수정
    if 'status' in data:
        status = data['status']
        valid_statuses = ['pending', 'approved', 'rejected', 'used']
        if status not in valid_statuses:
            raise ValidationError(f'Status must be one of: {", ".join(valid_statuses)}')
        inspiration.status = status

    db.session.commit()

    return jsonify({
        'message': 'Inspiration updated successfully',
        'inspiration': inspiration.to_dict()
    }), 200


@inspirations_bp.route('/<int:inspiration_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_inspiration(inspiration_id: int):
    """
    Inspiration 삭제 (Admin만)

    Args:
        inspiration_id: Inspiration ID

    Returns:
        성공 메시지
    """
    current_user_id = get_jwt_identity()

    inspiration = Inspiration.query.get(inspiration_id)
    if not inspiration:
        raise NotFoundError(f'Inspiration {inspiration_id} not found')

    # Draft가 연결되어 있으면 삭제 방지
    if inspiration.draft_id:
        raise ValidationError('Cannot delete inspiration with linked draft')

    db.session.delete(inspiration)
    db.session.commit()

    return jsonify({
        'message': 'Inspiration deleted successfully'
    }), 200


@inspirations_bp.route('/<int:inspiration_id>/approve', methods=['POST'])
@jwt_required()
@editor_required
def approve_inspiration(inspiration_id: int):
    """
    Inspiration 승인 (Editor 이상)

    Args:
        inspiration_id: Inspiration ID

    Returns:
        승인된 Inspiration 객체
    """
    current_user_id = get_jwt_identity()

    inspiration = Inspiration.query.get(inspiration_id)
    if not inspiration:
        raise NotFoundError(f'Inspiration {inspiration_id} not found')

    inspiration.status = 'approved'
    db.session.commit()

    return jsonify({
        'message': 'Inspiration approved successfully',
        'inspiration': inspiration.to_dict()
    }), 200


@inspirations_bp.route('/<int:inspiration_id>/reject', methods=['POST'])
@jwt_required()
@editor_required
def reject_inspiration(inspiration_id: int):
    """
    Inspiration 거부 (Editor 이상)

    Args:
        inspiration_id: Inspiration ID

    Request:
        {
            "reason": str  # 거부 사유 (선택)
        }

    Returns:
        거부된 Inspiration 객체
    """
    current_user_id = get_jwt_identity()

    inspiration = Inspiration.query.get(inspiration_id)
    if not inspiration:
        raise NotFoundError(f'Inspiration {inspiration_id} not found')

    data = request.get_json() or {}
    reason = data.get('reason', '')

    inspiration.status = 'rejected'
    if reason:
        inspiration.notes = f"Rejected: {reason}"

    db.session.commit()

    return jsonify({
        'message': 'Inspiration rejected successfully',
        'inspiration': inspiration.to_dict()
    }), 200


@inspirations_bp.route('/<int:inspiration_id>/create-draft', methods=['POST'])
@jwt_required()
def create_draft_from_inspiration(inspiration_id: int):
    """
    Inspiration으로부터 Draft 생성

    Args:
        inspiration_id: Inspiration ID

    Request:
        {
            "category_id": int,          # 카테고리 ID (필수)
            "writing_style_id": int,     # 작성 스타일 ID (선택)
            "generate_content": bool,    # AI 콘텐츠 생성 여부 (선택, 기본: false)
            "humor_style": str          # 유머 스타일 (선택)
        }

    Returns:
        생성된 Draft 객체
    """
    current_user_id = get_jwt_identity()

    inspiration = Inspiration.query.get(inspiration_id)
    if not inspiration:
        raise NotFoundError(f'Inspiration {inspiration_id} not found')

    # 이미 Draft가 생성되었는지 확인
    if inspiration.draft_id:
        raise ValidationError('Draft already exists for this inspiration')

    data = request.get_json()
    if not data:
        raise ValidationError('Request body is required')

    # 필수 필드 검증
    category_id = data.get('category_id')
    if not category_id:
        raise ValidationError('category_id is required')

    category = Category.query.get(category_id)
    if not category:
        raise NotFoundError(f'Category {category_id} not found')

    # 선택 필드
    writing_style_id = data.get('writing_style_id')
    generate_content = data.get('generate_content', False)
    humor_style = data.get('humor_style')

    # Draft 생성
    if generate_content:
        # AI로 콘텐츠 생성
        content_generator = ContentGenerator()
        result = content_generator.generate_from_inspiration(
            inspiration=inspiration,
            humor_style=humor_style
        )

        draft = Draft.create(
            user_id=current_user_id,
            category_id=category_id,
            inspiration_id=inspiration.id,
            title=inspiration.source.title if inspiration.source else 'Untitled',
            content=result.content,
            writing_style_id=writing_style_id,
            ai_generated=True
        )
    else:
        # 빈 Draft 생성 (수동 작성)
        draft = Draft.create(
            user_id=current_user_id,
            category_id=category_id,
            inspiration_id=inspiration.id,
            title=inspiration.source.title if inspiration.source else 'Untitled',
            content=f"# {inspiration.source.title if inspiration.source else 'Untitled'}\n\n{inspiration.concept}\n\n<!-- 여기에 콘텐츠를 작성하세요 -->",
            writing_style_id=writing_style_id,
            ai_generated=False
        )

    # Inspiration에 Draft 연결
    inspiration.draft_id = draft.id
    inspiration.status = 'used'

    db.session.commit()

    return jsonify({
        'message': 'Draft created successfully from inspiration',
        'draft': draft.to_dict(),
        'inspiration': inspiration.to_dict()
    }), 201


@inspirations_bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_statistics():
    """
    Inspiration 통계 조회

    Returns:
        {
            "total": int,
            "by_status": {...},
            "by_platform": {...},
            "avg_similarity": float,
            "with_draft": int,
            "without_draft": int
        }
    """
    current_user_id = get_jwt_identity()

    # 전체 개수
    total = Inspiration.query.count()

    # 상태별 개수
    by_status = {}
    for status in ['pending', 'approved', 'rejected', 'used']:
        count = Inspiration.query.filter_by(status=status).count()
        by_status[status] = count

    # 플랫폼별 개수
    from sqlalchemy import func
    platform_stats = db.session.query(
        Source.platform,
        func.count(Inspiration.id)
    ).join(Inspiration).group_by(Source.platform).all()

    by_platform = {platform: count for platform, count in platform_stats}

    # 평균 유사도
    avg_similarity = db.session.query(
        func.avg(Inspiration.similarity_score)
    ).scalar() or 0.0

    # Draft 연결 여부
    with_draft = Inspiration.query.filter(Inspiration.draft_id.isnot(None)).count()
    without_draft = Inspiration.query.filter(Inspiration.draft_id.is_(None)).count()

    return jsonify({
        'total': total,
        'by_status': by_status,
        'by_platform': by_platform,
        'avg_similarity': float(avg_similarity),
        'with_draft': with_draft,
        'without_draft': without_draft
    }), 200


@inspirations_bp.route('/batch-approve', methods=['POST'])
@jwt_required()
@editor_required
def batch_approve():
    """
    여러 Inspiration 일괄 승인 (Editor 이상)

    Request:
        {
            "inspiration_ids": [int]  # Inspiration ID 목록
        }

    Returns:
        {
            "message": str,
            "approved_count": int
        }
    """
    current_user_id = get_jwt_identity()

    data = request.get_json()
    if not data:
        raise ValidationError('Request body is required')

    inspiration_ids = data.get('inspiration_ids', [])
    if not inspiration_ids or not isinstance(inspiration_ids, list):
        raise ValidationError('inspiration_ids must be a non-empty list')

    # Inspiration 조회 및 승인
    inspirations = Inspiration.query.filter(Inspiration.id.in_(inspiration_ids)).all()

    approved_count = 0
    for inspiration in inspirations:
        if inspiration.status == 'pending':
            inspiration.status = 'approved'
            approved_count += 1

    db.session.commit()

    return jsonify({
        'message': f'{approved_count} inspirations approved successfully',
        'approved_count': approved_count
    }), 200


@inspirations_bp.route('/batch-reject', methods=['POST'])
@jwt_required()
@editor_required
def batch_reject():
    """
    여러 Inspiration 일괄 거부 (Editor 이상)

    Request:
        {
            "inspiration_ids": [int],  # Inspiration ID 목록
            "reason": str             # 거부 사유 (선택)
        }

    Returns:
        {
            "message": str,
            "rejected_count": int
        }
    """
    current_user_id = get_jwt_identity()

    data = request.get_json()
    if not data:
        raise ValidationError('Request body is required')

    inspiration_ids = data.get('inspiration_ids', [])
    if not inspiration_ids or not isinstance(inspiration_ids, list):
        raise ValidationError('inspiration_ids must be a non-empty list')

    reason = data.get('reason', '')

    # Inspiration 조회 및 거부
    inspirations = Inspiration.query.filter(Inspiration.id.in_(inspiration_ids)).all()

    rejected_count = 0
    for inspiration in inspirations:
        if inspiration.status == 'pending':
            inspiration.status = 'rejected'
            if reason:
                inspiration.notes = f"Rejected: {reason}"
            rejected_count += 1

    db.session.commit()

    return jsonify({
        'message': f'{rejected_count} inspirations rejected successfully',
        'rejected_count': rejected_count
    }), 200
