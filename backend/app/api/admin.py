"""
Admin API

관리자 전용 엔드포인트:
- 스케줄러 관리
- 시스템 통계
- 크롤링 작업 제어
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.utils.errors import NotFoundError, ValidationError
from app.utils.decorators import admin_required
from app.services.scheduler import get_scheduler
from app.services.reddit_crawler import RedditCrawler
from app.config import Settings

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/scheduler/status', methods=['GET'])
@jwt_required()
@admin_required
def get_scheduler_status():
    """
    스케줄러 상태 조회

    Returns:
        - running: 실행 중 여부
        - total_jobs: 전체 작업 수
        - active_jobs: 활성 작업 수
        - jobs: 작업 목록
    """
    scheduler = get_scheduler()

    if not scheduler:
        return jsonify({
            'running': False,
            'message': 'Scheduler not initialized (debug/testing mode)'
        }), 200

    stats = scheduler.get_statistics()
    jobs = scheduler.get_jobs()

    return jsonify({
        'running': stats['running'],
        'total_jobs': stats['total_jobs'],
        'active_jobs': stats['active_jobs'],
        'recent_24h': stats['recent_24h'],
        'jobs': jobs
    }), 200


@admin_bp.route('/scheduler/jobs', methods=['GET'])
@jwt_required()
@admin_required
def list_jobs():
    """
    모든 작업 목록 조회

    Returns:
        작업 목록
    """
    scheduler = get_scheduler()

    if not scheduler:
        return jsonify({'jobs': []}), 200

    jobs = scheduler.get_jobs()
    return jsonify({'jobs': jobs}), 200


@admin_bp.route('/scheduler/jobs/<job_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_job(job_id: str):
    """
    특정 작업 상세 조회

    Args:
        job_id: Job ID

    Returns:
        작업 정보 및 히스토리
    """
    scheduler = get_scheduler()

    if not scheduler:
        raise NotFoundError('Scheduler not initialized')

    # 작업 정보
    jobs = scheduler.get_jobs()
    job = next((j for j in jobs if j['id'] == job_id), None)

    if not job:
        raise NotFoundError(f'Job {job_id} not found')

    # 히스토리
    history = scheduler.get_job_history(job_id=job_id, limit=10)

    return jsonify({
        'job': job,
        'history': history
    }), 200


@admin_bp.route('/scheduler/jobs/<job_id>/run', methods=['POST'])
@jwt_required()
@admin_required
def run_job_now(job_id: str):
    """
    작업 즉시 실행

    Args:
        job_id: Job ID

    Returns:
        성공 메시지
    """
    scheduler = get_scheduler()

    if not scheduler:
        raise NotFoundError('Scheduler not initialized')

    success = scheduler.run_job_now(job_id)

    if not success:
        raise NotFoundError(f'Job {job_id} not found')

    return jsonify({
        'message': f'Job {job_id} scheduled to run immediately'
    }), 200


@admin_bp.route('/scheduler/jobs/<job_id>/pause', methods=['POST'])
@jwt_required()
@admin_required
def pause_job(job_id: str):
    """
    작업 일시 정지

    Args:
        job_id: Job ID

    Returns:
        성공 메시지
    """
    scheduler = get_scheduler()

    if not scheduler:
        raise NotFoundError('Scheduler not initialized')

    success = scheduler.pause_job(job_id)

    if not success:
        raise NotFoundError(f'Job {job_id} not found')

    return jsonify({
        'message': f'Job {job_id} paused'
    }), 200


@admin_bp.route('/scheduler/jobs/<job_id>/resume', methods=['POST'])
@jwt_required()
@admin_required
def resume_job(job_id: str):
    """
    작업 재개

    Args:
        job_id: Job ID

    Returns:
        성공 메시지
    """
    scheduler = get_scheduler()

    if not scheduler:
        raise NotFoundError('Scheduler not initialized')

    success = scheduler.resume_job(job_id)

    if not success:
        raise NotFoundError(f'Job {job_id} not found')

    return jsonify({
        'message': f'Job {job_id} resumed'
    }), 200


@admin_bp.route('/scheduler/history', methods=['GET'])
@jwt_required()
@admin_required
def get_job_history():
    """
    작업 실행 히스토리 조회

    Query Parameters:
        - job_id: 특정 작업 필터 (선택)
        - limit: 최대 개수 (기본: 20)

    Returns:
        히스토리 목록
    """
    scheduler = get_scheduler()

    if not scheduler:
        return jsonify({'history': []}), 200

    job_id = request.args.get('job_id')
    limit = request.args.get('limit', 20, type=int)
    limit = min(limit, 100)  # 최대 100

    history = scheduler.get_job_history(job_id=job_id, limit=limit)

    return jsonify({'history': history}), 200


@admin_bp.route('/crawler/collect-now', methods=['POST'])
@jwt_required()
@admin_required
def trigger_collection():
    """
    Reddit 수집 즉시 실행

    Request Body:
        - subreddits: Subreddit 목록 (선택)
        - limit_per_subreddit: subreddit당 개수 (기본: 10)
        - time_filter: 시간 필터 (기본: 'day')

    Returns:
        수집 결과
    """
    data = request.get_json() or {}

    subreddits = data.get('subreddits')
    limit_per_subreddit = data.get('limit_per_subreddit', 10)
    time_filter = data.get('time_filter', 'day')

    # Validation
    if limit_per_subreddit > 25:
        raise ValidationError('limit_per_subreddit must be <= 25')

    if time_filter not in ['hour', 'day', 'week', 'month', 'year', 'all']:
        raise ValidationError('Invalid time_filter')

    # Reddit 크롤러
    settings = Settings()
    crawler = RedditCrawler(
        client_id=settings.REDDIT_CLIENT_ID,
        client_secret=settings.REDDIT_CLIENT_SECRET
    )

    if not crawler.connect():
        raise Exception('Failed to connect to Reddit API')

    # 수집 실행
    result = crawler.collect_from_subreddits(
        subreddit_names=subreddits,
        limit_per_subreddit=limit_per_subreddit,
        time_filter=time_filter,
        create_inspirations=True
    )

    return jsonify({
        'message': 'Collection completed',
        'sources_created': result['sources_created'],
        'inspirations_created': result['inspirations_created']
    }), 200


@admin_bp.route('/crawler/statistics', methods=['GET'])
@jwt_required()
@admin_required
def get_crawler_statistics():
    """
    크롤러 통계 조회

    Returns:
        크롤러 통계
    """
    settings = Settings()
    crawler = RedditCrawler(
        client_id=settings.REDDIT_CLIENT_ID,
        client_secret=settings.REDDIT_CLIENT_SECRET
    )

    stats = crawler.get_statistics()

    return jsonify(stats), 200
