"""
A/B 테스팅 API
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from app import db
from app.models.ab_test import ABTest, ABTestAssignment, ABTestEvent
from datetime import datetime


ab_test_bp = Blueprint('ab_test', __name__)


def get_session_id():
    """세션 ID 가져오기"""
    return request.headers.get('X-Session-ID')


def get_user_id():
    """현재 사용자 ID 가져오기 (인증된 경우만)"""
    try:
        verify_jwt_in_request(optional=True)
        return get_jwt_identity()
    except:
        return None


@ab_test_bp.route('/variant/<test_name>', methods=['GET'])
def get_variant(test_name):
    """
    테스트 변형 조회/할당

    Returns:
        {
            "success": true,
            "data": {
                "test_name": "homepage_layout",
                "variant": "control",
                "variant_info": {...}
            }
        }
    """
    try:
        test = ABTest.query.filter_by(name=test_name, status='running').first()

        if not test:
            return jsonify({
                'success': False,
                'error': 'Test not found or not running'
            }), 404

        user_id = get_user_id()
        session_id = get_session_id()

        # 기존 할당 확인 또는 새로 할당
        variant = test.get_variant(user_id=user_id, session_id=session_id)

        if not variant:
            variant = test.assign_variant(user_id=user_id, session_id=session_id)

        variant_info = test.variants.get(variant, {})

        return jsonify({
            'success': True,
            'data': {
                'test_name': test.name,
                'variant': variant,
                'variant_info': variant_info
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ab_test_bp.route('/event', methods=['POST'])
def track_event():
    """
    A/B 테스트 이벤트 추적

    Request Body:
        {
            "test_name": "homepage_layout",
            "event_type": "click",
            "value": 1.0,
            "metadata": {...}
        }

    Returns:
        {
            "success": true
        }
    """
    try:
        data = request.get_json()

        test_name = data.get('test_name')
        event_type = data.get('event_type')

        if not test_name or not event_type:
            return jsonify({
                'success': False,
                'error': 'test_name and event_type are required'
            }), 400

        test = ABTest.query.filter_by(name=test_name).first()
        if not test:
            return jsonify({
                'success': False,
                'error': 'Test not found'
            }), 404

        user_id = get_user_id()
        session_id = get_session_id()

        # 할당 조회
        assignment = ABTestAssignment.query.filter_by(
            test_id=test.id,
            user_id=user_id,
            session_id=session_id
        ).first()

        if not assignment:
            return jsonify({
                'success': False,
                'error': 'No assignment found for this test'
            }), 404

        # 이벤트 생성
        event = ABTestEvent(
            assignment_id=assignment.id,
            event_type=event_type,
            value=data.get('value'),
            metadata=data.get('metadata')
        )

        db.session.add(event)
        db.session.commit()

        return jsonify({'success': True})

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ab_test_bp.route('/tests', methods=['GET'])
@jwt_required()
def list_tests():
    """
    A/B 테스트 목록 조회 (관리자용)

    Returns:
        {
            "success": true,
            "data": {
                "tests": [...]
            }
        }
    """
    # TODO: 관리자 권한 확인

    tests = ABTest.query.all()

    return jsonify({
        'success': True,
        'data': {
            'tests': [test.to_dict() for test in tests]
        }
    })


@ab_test_bp.route('/tests', methods=['POST'])
@jwt_required()
def create_test():
    """
    A/B 테스트 생성 (관리자용)

    Request Body:
        {
            "name": "homepage_layout",
            "description": "Test new homepage layout",
            "variants": {
                "control": {"name": "Original", "weight": 50},
                "variant_a": {"name": "New Design", "weight": 50}
            },
            "goal_metric": "click_rate"
        }

    Returns:
        {
            "success": true,
            "data": {...}
        }
    """
    # TODO: 관리자 권한 확인

    try:
        data = request.get_json()

        if not data.get('name') or not data.get('variants'):
            return jsonify({
                'success': False,
                'error': 'name and variants are required'
            }), 400

        test = ABTest(
            name=data['name'],
            description=data.get('description'),
            variants=data['variants'],
            goal_metric=data.get('goal_metric')
        )

        db.session.add(test)
        db.session.commit()

        return jsonify({
            'success': True,
            'data': test.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ab_test_bp.route('/tests/<int:test_id>/start', methods='POST')
@jwt_required()
def start_test(test_id):
    """테스트 시작 (관리자용)"""
    # TODO: 관리자 권한 확인

    test = ABTest.query.get_or_404(test_id)

    if test.status != 'draft':
        return jsonify({
            'success': False,
            'error': 'Test must be in draft status'
        }), 400

    test.status = 'running'
    test.started_at = datetime.utcnow()

    db.session.commit()

    return jsonify({
        'success': True,
        'data': test.to_dict()
    })


@ab_test_bp.route('/tests/<int:test_id>/stop', methods=['POST'])
@jwt_required()
def stop_test(test_id):
    """테스트 종료 (관리자용)"""
    # TODO: 관리자 권한 확인

    test = ABTest.query.get_or_404(test_id)

    if test.status != 'running':
        return jsonify({
            'success': False,
            'error': 'Test must be running'
        }), 400

    test.status = 'completed'
    test.ended_at = datetime.utcnow()

    db.session.commit()

    return jsonify({
        'success': True,
        'data': test.to_dict()
    })


@ab_test_bp.route('/tests/<int:test_id>/results', methods=['GET'])
@jwt_required()
def get_test_results(test_id):
    """
    A/B 테스트 결과 조회 (관리자용)

    Returns:
        {
            "success": true,
            "data": {
                "test": {...},
                "results": {
                    "control": {...},
                    "variant_a": {...}
                }
            }
        }
    """
    # TODO: 관리자 권한 확인

    test = ABTest.query.get_or_404(test_id)

    # 각 변형별 통계
    results = {}

    for variant_key in test.variants.keys():
        # 해당 변형의 할당 수
        assignments_count = ABTestAssignment.query.filter_by(
            test_id=test.id,
            variant=variant_key
        ).count()

        # 이벤트 통계
        events_query = db.session.query(
            ABTestEvent.event_type,
            db.func.count(ABTestEvent.id).label('count'),
            db.func.avg(ABTestEvent.value).label('avg_value')
        ).join(ABTestAssignment).filter(
            ABTestAssignment.test_id == test.id,
            ABTestAssignment.variant == variant_key
        ).group_by(ABTestEvent.event_type).all()

        events_stats = {
            event_type: {
                'count': count,
                'avg_value': float(avg_value) if avg_value else None
            }
            for event_type, count, avg_value in events_query
        }

        results[variant_key] = {
            'assignments': assignments_count,
            'events': events_stats
        }

    return jsonify({
        'success': True,
        'data': {
            'test': test.to_dict(),
            'results': results
        }
    })
