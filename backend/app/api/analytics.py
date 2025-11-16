"""
Analytics API

통계 및 분석 엔드포인트:
- 전체 시스템 통계
- 콘텐츠 생성 통계
- 사용자 활동 통계
- 플랫폼별 분석
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import func
from datetime import datetime, timedelta

from app import db
from app.models import (
    User, Post, Draft, Source, Inspiration,
    Category, Tag, WritingStyle
)
from app.utils.decorators import admin_required, editor_required

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/overview', methods=['GET'])
@jwt_required()
@editor_required
def get_overview():
    """
    전체 시스템 개요

    Returns:
        {
            "users": {...},
            "content": {...},
            "sources": {...},
            "activity": {...}
        }
    """
    # 사용자 통계
    total_users = User.query.count()
    users_by_role = {}
    for role in ['user', 'editor', 'admin']:
        count = User.query.filter_by(role=role).count()
        users_by_role[role] = count

    # 콘텐츠 통계
    total_posts = Post.query.count()
    published_posts = Post.query.filter_by(status='published').count()
    total_drafts = Draft.query.count()
    ai_generated_drafts = Draft.query.filter_by(ai_generated=True).count()

    # 소스 통계
    total_sources = Source.query.count()
    total_inspirations = Inspiration.query.count()
    approved_inspirations = Inspiration.query.filter_by(status='approved').count()

    # 최근 활동 (7일)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_posts = Post.query.filter(Post.created_at >= seven_days_ago).count()
    recent_drafts = Draft.query.filter(Draft.created_at >= seven_days_ago).count()

    return jsonify({
        'users': {
            'total': total_users,
            'by_role': users_by_role
        },
        'content': {
            'total_posts': total_posts,
            'published_posts': published_posts,
            'total_drafts': total_drafts,
            'ai_generated_drafts': ai_generated_drafts,
            'manual_drafts': total_drafts - ai_generated_drafts
        },
        'sources': {
            'total_sources': total_sources,
            'total_inspirations': total_inspirations,
            'approved_inspirations': approved_inspirations
        },
        'activity': {
            'recent_posts_7d': recent_posts,
            'recent_drafts_7d': recent_drafts
        }
    }), 200


@analytics_bp.route('/content-stats', methods=['GET'])
@jwt_required()
@editor_required
def get_content_stats():
    """
    콘텐츠 생성 통계

    Query Parameters:
        days (int): 조회 기간 (기본: 30일)

    Returns:
        {
            "period": str,
            "posts": {...},
            "drafts": {...},
            "categories": {...}
        }
    """
    days = min(request.args.get('days', 30, type=int), 365)
    start_date = datetime.utcnow() - timedelta(days=days)

    # Post 통계
    posts_created = Post.query.filter(Post.created_at >= start_date).count()
    posts_published = Post.query.filter(
        Post.published_at >= start_date,
        Post.status == 'published'
    ).count()

    # Draft 통계
    drafts_created = Draft.query.filter(Draft.created_at >= start_date).count()
    ai_drafts = Draft.query.filter(
        Draft.created_at >= start_date,
        Draft.ai_generated == True
    ).count()

    # 카테고리별 통계
    category_stats = db.session.query(
        Category.name,
        func.count(Post.id).label('count')
    ).join(Post).filter(
        Post.created_at >= start_date
    ).group_by(Category.name).all()

    categories = {name: count for name, count in category_stats}

    return jsonify({
        'period': f'{days} days',
        'posts': {
            'created': posts_created,
            'published': posts_published
        },
        'drafts': {
            'total_created': drafts_created,
            'ai_generated': ai_drafts,
            'manual': drafts_created - ai_drafts
        },
        'by_category': categories
    }), 200


@analytics_bp.route('/user-activity', methods=['GET'])
@jwt_required()
@admin_required
def get_user_activity():
    """
    사용자 활동 통계 (Admin만)

    Returns:
        {
            "top_contributors": [...],
            "activity_by_user": {...}
        }
    """
    # 상위 기여자 (Post 수 기준)
    top_contributors = db.session.query(
        User.username,
        func.count(Post.id).label('post_count')
    ).join(Post).group_by(User.username).order_by(
        func.count(Post.id).desc()
    ).limit(10).all()

    contributors = [
        {'username': username, 'post_count': count}
        for username, count in top_contributors
    ]

    # Draft 생성 통계
    draft_stats = db.session.query(
        User.username,
        func.count(Draft.id).label('draft_count')
    ).join(Draft).group_by(User.username).all()

    drafts_by_user = {username: count for username, count in draft_stats}

    return jsonify({
        'top_contributors': contributors,
        'drafts_by_user': drafts_by_user
    }), 200


@analytics_bp.route('/sources-stats', methods=['GET'])
@jwt_required()
@editor_required
def get_sources_stats():
    """
    소스 및 Inspiration 통계

    Returns:
        {
            "by_platform": {...},
            "inspiration_conversion": float,
            "avg_similarity": float
        }
    """
    # 플랫폼별 소스 수
    platform_stats = db.session.query(
        Source.platform,
        func.count(Source.id).label('count')
    ).group_by(Source.platform).all()

    by_platform = {platform: count for platform, count in platform_stats}

    # Inspiration 전환율
    total_sources = Source.query.count()
    sources_with_inspiration = db.session.query(Source).join(Inspiration).distinct().count()
    conversion_rate = (sources_with_inspiration / total_sources * 100) if total_sources > 0 else 0.0

    # 평균 유사도
    avg_similarity = db.session.query(func.avg(Inspiration.similarity_score)).scalar() or 0.0

    return jsonify({
        'by_platform': by_platform,
        'inspiration_conversion': float(conversion_rate),
        'avg_similarity': float(avg_similarity)
    }), 200


@analytics_bp.route('/trends', methods=['GET'])
@jwt_required()
@editor_required
def get_trends():
    """
    트렌드 분석 (최근 30일)

    Returns:
        {
            "daily_posts": [...],
            "daily_drafts": [...],
            "popular_categories": [...],
            "popular_tags": [...]
        }
    """
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    # 일별 Post 생성 수
    daily_posts = db.session.query(
        func.date(Post.created_at).label('date'),
        func.count(Post.id).label('count')
    ).filter(Post.created_at >= thirty_days_ago).group_by(
        func.date(Post.created_at)
    ).all()

    posts_trend = [
        {'date': str(date), 'count': count}
        for date, count in daily_posts
    ]

    # 일별 Draft 생성 수
    daily_drafts = db.session.query(
        func.date(Draft.created_at).label('date'),
        func.count(Draft.id).label('count')
    ).filter(Draft.created_at >= thirty_days_ago).group_by(
        func.date(Draft.created_at)
    ).all()

    drafts_trend = [
        {'date': str(date), 'count': count}
        for date, count in daily_drafts
    ]

    # 인기 카테고리
    popular_categories = db.session.query(
        Category.name,
        func.count(Post.id).label('count')
    ).join(Post).filter(Post.created_at >= thirty_days_ago).group_by(
        Category.name
    ).order_by(func.count(Post.id).desc()).limit(10).all()

    categories = [
        {'name': name, 'count': count}
        for name, count in popular_categories
    ]

    # 인기 태그
    from app.models.tag import post_tags
    popular_tags = db.session.query(
        Tag.name,
        func.count(post_tags.c.post_id).label('count')
    ).join(post_tags).join(Post).filter(
        Post.created_at >= thirty_days_ago
    ).group_by(Tag.name).order_by(
        func.count(post_tags.c.post_id).desc()
    ).limit(10).all()

    tags = [
        {'name': name, 'count': count}
        for name, count in popular_tags
    ]

    return jsonify({
        'daily_posts': posts_trend,
        'daily_drafts': drafts_trend,
        'popular_categories': categories,
        'popular_tags': tags
    }), 200
