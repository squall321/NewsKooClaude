"""
고급 검색 API
전체 텍스트 검색, 필터링, 자동완성
"""

from flask import Blueprint, request, jsonify
from sqlalchemy import or_, and_, func, desc
from app.models import Post, Category, Tag, User
from app import db, cache
from datetime import datetime, timedelta


search_bp = Blueprint('search', __name__, url_prefix='/api/search')


@search_bp.route('/', methods=['GET'])
@cache.cached(timeout=60, query_string=True)
def search_posts():
    """
    게시물 검색

    Query Parameters:
        q: 검색어 (required)
        category: 카테고리 ID
        tags: 태그 목록 (쉼표로 구분)
        date_from: 시작 날짜 (YYYY-MM-DD)
        date_to: 종료 날짜 (YYYY-MM-DD)
        sort: 정렬 기준 (relevance, date, views, likes)
        order: 정렬 순서 (asc, desc)
        page: 페이지 번호 (default: 1)
        per_page: 페이지당 항목 수 (default: 20)

    Returns:
        {
            "success": true,
            "data": {
                "posts": [...],
                "total": 100,
                "page": 1,
                "per_page": 20,
                "pages": 5
            }
        }
    """
    # 검색어
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({
            'success': False,
            'error': 'Search query is required'
        }), 400

    # 필터 파라미터
    category_id = request.args.get('category', type=int)
    tags = request.args.get('tags', '').split(',') if request.args.get('tags') else []
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')

    # 정렬 파라미터
    sort = request.args.get('sort', 'relevance')
    order = request.args.get('order', 'desc')

    # 페이지네이션
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)

    # 기본 쿼리 (게시된 게시물만)
    posts_query = Post.query.filter_by(status='published')

    # 전체 텍스트 검색 (제목 + 내용)
    search_filter = or_(
        Post.title.ilike(f'%{query}%'),
        Post.content.ilike(f'%{query}%'),
        Post.translated_title.ilike(f'%{query}%'),
        Post.translated_content.ilike(f'%{query}%')
    )
    posts_query = posts_query.filter(search_filter)

    # 카테고리 필터
    if category_id:
        posts_query = posts_query.filter_by(category_id=category_id)

    # 태그 필터
    if tags and tags[0]:  # 빈 문자열 제외
        for tag_name in tags:
            tag_name = tag_name.strip()
            if tag_name:
                posts_query = posts_query.join(Post.tags).filter(Tag.name == tag_name)

    # 날짜 범위 필터
    if date_from:
        try:
            from_date = datetime.strptime(date_from, '%Y-%m-%d')
            posts_query = posts_query.filter(Post.created_at >= from_date)
        except ValueError:
            pass

    if date_to:
        try:
            to_date = datetime.strptime(date_to, '%Y-%m-%d')
            # 하루의 끝까지 포함
            to_date = to_date.replace(hour=23, minute=59, second=59)
            posts_query = posts_query.filter(Post.created_at <= to_date)
        except ValueError:
            pass

    # 정렬
    if sort == 'date':
        posts_query = posts_query.order_by(
            desc(Post.created_at) if order == 'desc' else Post.created_at
        )
    elif sort == 'views':
        posts_query = posts_query.order_by(
            desc(Post.views) if order == 'desc' else Post.views
        )
    elif sort == 'likes':
        posts_query = posts_query.order_by(
            desc(Post.likes_count) if order == 'desc' else Post.likes_count
        )
    else:  # relevance (기본값)
        # 간단한 관련성 점수: 제목 매칭 우선, 최신순
        posts_query = posts_query.order_by(
            desc(
                func.case(
                    (Post.title.ilike(f'%{query}%'), 2),
                    (Post.translated_title.ilike(f'%{query}%'), 1),
                    else_=0
                ) + func.case(
                    (Post.created_at > datetime.now() - timedelta(days=7), 1),
                    else_=0
                )
            )
        )

    # 페이지네이션
    pagination = posts_query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    # 결과 직렬화
    posts_data = [{
        'id': post.id,
        'title': post.translated_title or post.title,
        'content': post.translated_content[:200] + '...' if post.translated_content else '',
        'slug': post.slug,
        'image_url': post.image_url,
        'category': {
            'id': post.category.id,
            'name': post.category.name
        } if post.category else None,
        'tags': [{'id': tag.id, 'name': tag.name} for tag in post.tags],
        'views': post.views,
        'likes_count': post.likes_count,
        'comments_count': post.comments.count() if hasattr(post, 'comments') else 0,
        'created_at': post.created_at.isoformat(),
    } for post in pagination.items]

    return jsonify({
        'success': True,
        'data': {
            'posts': posts_data,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }
    })


@search_bp.route('/autocomplete', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def autocomplete():
    """
    검색어 자동완성

    Query Parameters:
        q: 검색어 (required)
        limit: 결과 개수 (default: 10)

    Returns:
        {
            "success": true,
            "data": {
                "suggestions": ["검색어1", "검색어2", ...]
            }
        }
    """
    query = request.args.get('q', '').strip()
    if not query or len(query) < 2:
        return jsonify({
            'success': True,
            'data': {'suggestions': []}
        })

    limit = min(request.args.get('limit', 10, type=int), 20)

    # 제목에서 자동완성 검색
    posts = Post.query.filter(
        Post.status == 'published',
        or_(
            Post.title.ilike(f'{query}%'),
            Post.translated_title.ilike(f'{query}%')
        )
    ).limit(limit * 2).all()

    # 중복 제거 및 정렬
    suggestions = []
    seen = set()

    for post in posts:
        titles = [post.translated_title or post.title, post.title]
        for title in titles:
            if title and title.lower() not in seen:
                if query.lower() in title.lower():
                    suggestions.append(title)
                    seen.add(title.lower())
                    if len(suggestions) >= limit:
                        break
        if len(suggestions) >= limit:
            break

    return jsonify({
        'success': True,
        'data': {'suggestions': suggestions[:limit]}
    })


@search_bp.route('/filters', methods=['GET'])
@cache.cached(timeout=600)
def get_filters():
    """
    검색 필터 옵션 조회

    Returns:
        {
            "success": true,
            "data": {
                "categories": [...],
                "tags": [...],
                "date_ranges": [...]
            }
        }
    """
    # 카테고리 목록
    categories = Category.query.all()
    categories_data = [{
        'id': cat.id,
        'name': cat.name,
        'slug': cat.slug
    } for cat in categories]

    # 인기 태그 (상위 20개)
    popular_tags = Tag.query.join(Tag.posts).group_by(Tag.id).order_by(
        desc(func.count(Post.id))
    ).limit(20).all()

    tags_data = [{
        'id': tag.id,
        'name': tag.name
    } for tag in popular_tags]

    # 날짜 범위 프리셋
    now = datetime.now()
    date_ranges = [
        {
            'label': '오늘',
            'value': 'today',
            'date_from': now.strftime('%Y-%m-%d'),
            'date_to': now.strftime('%Y-%m-%d')
        },
        {
            'label': '이번 주',
            'value': 'this_week',
            'date_from': (now - timedelta(days=now.weekday())).strftime('%Y-%m-%d'),
            'date_to': now.strftime('%Y-%m-%d')
        },
        {
            'label': '이번 달',
            'value': 'this_month',
            'date_from': now.replace(day=1).strftime('%Y-%m-%d'),
            'date_to': now.strftime('%Y-%m-%d')
        },
        {
            'label': '최근 7일',
            'value': 'last_7_days',
            'date_from': (now - timedelta(days=7)).strftime('%Y-%m-%d'),
            'date_to': now.strftime('%Y-%m-%d')
        },
        {
            'label': '최근 30일',
            'value': 'last_30_days',
            'date_from': (now - timedelta(days=30)).strftime('%Y-%m-%d'),
            'date_to': now.strftime('%Y-%m-%d')
        }
    ]

    return jsonify({
        'success': True,
        'data': {
            'categories': categories_data,
            'tags': tags_data,
            'date_ranges': date_ranges
        }
    })


@search_bp.route('/trending', methods=['GET'])
@cache.cached(timeout=1800)  # 30분 캐시
def trending_searches():
    """
    인기 검색어

    Returns:
        {
            "success": true,
            "data": {
                "trending": ["검색어1", "검색어2", ...]
            }
        }
    """
    # TODO: 실제로는 검색 로그를 분석하여 인기 검색어 추출
    # 현재는 인기 게시물 제목에서 추출

    popular_posts = Post.query.filter_by(status='published').order_by(
        desc(Post.views)
    ).limit(10).all()

    trending = [post.translated_title or post.title for post in popular_posts]

    return jsonify({
        'success': True,
        'data': {'trending': trending}
    })
