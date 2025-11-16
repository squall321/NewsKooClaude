"""
Source API

외부 소스 관리 엔드포인트:
- CRUD 작업
- 플랫폼별 필터링
- 통계 조회
- Inspiration 연동
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func

from app import db
from app.models import Source, Inspiration
from app.utils.errors import NotFoundError, ValidationError
from app.utils.decorators import admin_required, editor_required

sources_bp = Blueprint('sources', __name__)


@sources_bp.route('', methods=['GET'])
@jwt_required()
def list_sources():
    """
    Source 목록 조회

    Query Parameters:
        page (int): 페이지 번호 (기본: 1)
        per_page (int): 페이지당 항목 수 (기본: 20, 최대: 100)
        platform (str): 플랫폼 필터 ('reddit', 'twitter' 등)
        min_upvotes (int): 최소 upvotes
        min_comments (int): 최소 comments
        has_inspiration (bool): Inspiration 존재 여부
        sort_by (str): 정렬 기준 ('created_at', 'upvotes', 'comments')
        order (str): 정렬 순서 ('asc', 'desc')

    Returns:
        {
            "sources": [...],
            "pagination": {...}
        }
    """
    # 페이지네이션
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)

    # 필터링
    platform = request.args.get('platform')
    min_upvotes = request.args.get('min_upvotes', type=int)
    min_comments = request.args.get('min_comments', type=int)
    has_inspiration = request.args.get('has_inspiration', type=lambda v: v.lower() == 'true' if v else None)

    # 정렬
    sort_by = request.args.get('sort_by', 'created_at')
    order = request.args.get('order', 'desc')

    # 쿼리 생성
    query = Source.query

    # 필터 적용
    if platform:
        query = query.filter(Source.platform == platform)

    if min_upvotes is not None:
        query = query.filter(Source.upvotes >= min_upvotes)

    if min_comments is not None:
        query = query.filter(Source.comments >= min_comments)

    if has_inspiration is not None:
        if has_inspiration:
            query = query.join(Inspiration)
        else:
            query = query.outerjoin(Inspiration).filter(Inspiration.id.is_(None))

    # 정렬 적용
    if sort_by == 'created_at':
        sort_column = Source.created_at
    elif sort_by == 'upvotes':
        sort_column = Source.upvotes
    elif sort_by == 'comments':
        sort_column = Source.comments
    else:
        sort_column = Source.created_at

    if order == 'desc':
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # 페이지네이션 실행
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    # 응답 생성
    sources = []
    for source in pagination.items:
        sources.append(source.to_dict())

    return jsonify({
        'sources': sources,
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }), 200


@sources_bp.route('/<int:source_id>', methods=['GET'])
@jwt_required()
def get_source(source_id: int):
    """
    Source 상세 조회

    Args:
        source_id: Source ID

    Returns:
        Source 객체 및 연관된 Inspirations
    """
    source = Source.query.get(source_id)
    if not source:
        raise NotFoundError(f'Source {source_id} not found')

    # Source 정보
    source_dict = source.to_dict()

    # 연관된 Inspirations
    inspirations = Inspiration.query.filter_by(source_id=source_id).all()
    source_dict['inspirations'] = [insp.to_dict() for insp in inspirations]

    return jsonify(source_dict), 200


@sources_bp.route('/<int:source_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_source(source_id: int):
    """
    Source 삭제 (Admin만)

    Args:
        source_id: Source ID

    Returns:
        성공 메시지
    """
    source = Source.query.get(source_id)
    if not source:
        raise NotFoundError(f'Source {source_id} not found')

    # Inspiration이 연결되어 있으면 삭제 방지
    inspirations = Inspiration.query.filter_by(source_id=source_id).count()
    if inspirations > 0:
        raise ValidationError(f'Cannot delete source with {inspirations} linked inspirations')

    db.session.delete(source)
    db.session.commit()

    return jsonify({
        'message': 'Source deleted successfully'
    }), 200


@sources_bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_statistics():
    """
    Source 통계 조회

    Returns:
        {
            "total": int,
            "by_platform": {...},
            "avg_upvotes": float,
            "avg_comments": float,
            "with_inspiration": int,
            "without_inspiration": int
        }
    """
    # 전체 개수
    total = Source.query.count()

    # 플랫폼별 개수
    platform_stats = db.session.query(
        Source.platform,
        func.count(Source.id)
    ).group_by(Source.platform).all()

    by_platform = {platform: count for platform, count in platform_stats}

    # 평균 upvotes 및 comments
    avg_upvotes = db.session.query(func.avg(Source.upvotes)).scalar() or 0.0
    avg_comments = db.session.query(func.avg(Source.comments)).scalar() or 0.0

    # Inspiration 연결 여부
    with_inspiration = db.session.query(Source).join(Inspiration).distinct().count()
    without_inspiration = total - with_inspiration

    return jsonify({
        'total': total,
        'by_platform': by_platform,
        'avg_upvotes': float(avg_upvotes),
        'avg_comments': float(avg_comments),
        'with_inspiration': with_inspiration,
        'without_inspiration': without_inspiration
    }), 200


@sources_bp.route('/platforms', methods=['GET'])
@jwt_required()
def list_platforms():
    """
    사용 가능한 플랫폼 목록 조회

    Returns:
        {
            "platforms": [
                {
                    "name": str,
                    "count": int
                }
            ]
        }
    """
    platform_stats = db.session.query(
        Source.platform,
        func.count(Source.id).label('count')
    ).group_by(Source.platform).all()

    platforms = [
        {'name': platform, 'count': count}
        for platform, count in platform_stats
    ]

    return jsonify({
        'platforms': platforms
    }), 200


@sources_bp.route('/top', methods=['GET'])
@jwt_required()
def get_top_sources():
    """
    인기 소스 조회 (upvotes 기준)

    Query Parameters:
        limit (int): 반환할 개수 (기본: 10, 최대: 50)
        platform (str): 플랫폼 필터 (선택)

    Returns:
        {
            "sources": [...]
        }
    """
    limit = min(request.args.get('limit', 10, type=int), 50)
    platform = request.args.get('platform')

    query = Source.query

    if platform:
        query = query.filter(Source.platform == platform)

    sources = query.order_by(Source.upvotes.desc()).limit(limit).all()

    return jsonify({
        'sources': [source.to_dict() for source in sources]
    }), 200
