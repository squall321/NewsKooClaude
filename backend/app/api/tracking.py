"""
사용자 활동 추적 API
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from app import db
from app.models.user_activity import UserActivity, PageView, SearchLog
import uuid
from datetime import datetime


tracking_bp = Blueprint('tracking', __name__, url_prefix='/api/tracking')


def get_client_info():
    """클라이언트 정보 추출"""
    return {
        'ip_address': request.headers.get('X-Forwarded-For', request.remote_addr),
        'user_agent': request.headers.get('User-Agent', '')[:500],
        'referrer': request.headers.get('Referer', '')[:500]
    }


def get_session_id():
    """세션 ID 가져오기 또는 생성"""
    session_id = request.headers.get('X-Session-ID')
    if not session_id:
        session_id = str(uuid.uuid4())
    return session_id


def get_user_id():
    """현재 사용자 ID 가져오기 (인증된 경우만)"""
    try:
        verify_jwt_in_request(optional=True)
        return get_jwt_identity()
    except:
        return None


@tracking_bp.route('/activity', methods=['POST'])
def track_activity():
    """
    사용자 활동 추적

    Request Body:
        {
            "activity_type": "view",
            "resource_type": "post",
            "resource_id": 123,
            "action_detail": {...}
        }

    Returns:
        {
            "success": true,
            "session_id": "..."
        }
    """
    try:
        data = request.get_json()

        if not data or not data.get('activity_type'):
            return jsonify({
                'success': False,
                'error': 'activity_type is required'
            }), 400

        client_info = get_client_info()
        session_id = get_session_id()
        user_id = get_user_id()

        activity = UserActivity(
            user_id=user_id,
            session_id=session_id,
            ip_address=client_info['ip_address'],
            user_agent=client_info['user_agent'],
            activity_type=data.get('activity_type'),
            resource_type=data.get('resource_type'),
            resource_id=data.get('resource_id'),
            action_detail=data.get('action_detail'),
            referrer=client_info['referrer']
        )

        db.session.add(activity)
        db.session.commit()

        return jsonify({
            'success': True,
            'session_id': session_id
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@tracking_bp.route('/pageview', methods=['POST'])
def track_pageview():
    """
    페이지 조회 추적

    Request Body:
        {
            "path": "/post/hello-world",
            "title": "게시물 제목",
            "duration": 45  # 체류 시간 (초), 선택적
        }

    Returns:
        {
            "success": true,
            "session_id": "...",
            "pageview_id": 123
        }
    """
    try:
        data = request.get_json()

        if not data or not data.get('path'):
            return jsonify({
                'success': False,
                'error': 'path is required'
            }), 400

        client_info = get_client_info()
        session_id = get_session_id()
        user_id = get_user_id()

        # 같은 세션의 같은 경로 페이지뷰 업데이트 또는 새로 생성
        existing_view = PageView.query.filter_by(
            session_id=session_id,
            path=data['path']
        ).order_by(PageView.created_at.desc()).first()

        # 최근 5분 이내 같은 페이지 조회는 업데이트
        if existing_view and \
           (datetime.utcnow() - existing_view.created_at).seconds < 300:
            if data.get('duration'):
                existing_view.duration = data['duration']
                existing_view.updated_at = datetime.utcnow()

            db.session.commit()

            return jsonify({
                'success': True,
                'session_id': session_id,
                'pageview_id': existing_view.id,
                'updated': True
            })
        else:
            # 새 페이지뷰 생성
            pageview = PageView(
                user_id=user_id,
                session_id=session_id,
                ip_address=client_info['ip_address'],
                path=data['path'],
                title=data.get('title', '')[:200],
                referrer=client_info['referrer'],
                duration=data.get('duration')
            )

            db.session.add(pageview)
            db.session.commit()

            return jsonify({
                'success': True,
                'session_id': session_id,
                'pageview_id': pageview.id,
                'updated': False
            })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@tracking_bp.route('/search', methods=['POST'])
def track_search():
    """
    검색 로그 추적

    Request Body:
        {
            "query": "검색어",
            "results_count": 10,
            "filters": {...},
            "clicked_result_id": 123,
            "clicked_result_position": 3
        }

    Returns:
        {
            "success": true,
            "session_id": "..."
        }
    """
    try:
        data = request.get_json()

        if not data or not data.get('query'):
            return jsonify({
                'success': False,
                'error': 'query is required'
            }), 400

        session_id = get_session_id()
        user_id = get_user_id()

        search_log = SearchLog(
            user_id=user_id,
            session_id=session_id,
            query=data['query'],
            results_count=data.get('results_count'),
            filters=data.get('filters'),
            clicked_result_id=data.get('clicked_result_id'),
            clicked_result_position=data.get('clicked_result_position')
        )

        db.session.add(search_log)
        db.session.commit()

        return jsonify({
            'success': True,
            'session_id': session_id
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@tracking_bp.route('/analytics', methods=['GET'])
@jwt_required()
def get_user_analytics():
    """
    사용자 활동 분석 조회 (관리자용)

    Query Parameters:
        user_id: 사용자 ID (선택적)
        activity_type: 활동 타입 (선택적)
        date_from: 시작 날짜 (YYYY-MM-DD)
        date_to: 종료 날짜 (YYYY-MM-DD)
        limit: 결과 개수 (default: 100)

    Returns:
        {
            "success": true,
            "data": {
                "activities": [...],
                "summary": {...}
            }
        }
    """
    # TODO: 관리자 권한 확인
    current_user_id = get_jwt_identity()

    user_id = request.args.get('user_id', type=int)
    activity_type = request.args.get('activity_type')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    limit = min(request.args.get('limit', 100, type=int), 1000)

    # 쿼리 빌드
    query = UserActivity.query

    if user_id:
        query = query.filter_by(user_id=user_id)

    if activity_type:
        query = query.filter_by(activity_type=activity_type)

    if date_from:
        try:
            from_date = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(UserActivity.created_at >= from_date)
        except ValueError:
            pass

    if date_to:
        try:
            to_date = datetime.strptime(date_to, '%Y-%m-%d')
            query = query.filter(UserActivity.created_at <= to_date)
        except ValueError:
            pass

    # 최신순 정렬
    activities = query.order_by(UserActivity.created_at.desc()).limit(limit).all()

    # 요약 통계
    summary = {
        'total_activities': query.count(),
        'activity_types': db.session.query(
            UserActivity.activity_type,
            db.func.count(UserActivity.id)
        ).filter(
            UserActivity.id.in_([a.id for a in activities])
        ).group_by(UserActivity.activity_type).all()
    }

    return jsonify({
        'success': True,
        'data': {
            'activities': [a.to_dict() for a in activities],
            'summary': {
                'total': summary['total_activities'],
                'by_type': {at: count for at, count in summary['activity_types']}
            }
        }
    })
