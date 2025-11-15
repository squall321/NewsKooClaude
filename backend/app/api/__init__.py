"""
API Blueprint
모든 API 라우트를 관리하는 메인 블루프린트
"""
from flask import Blueprint

api_bp = Blueprint('api', __name__)

# Import routes (나중에 추가될 예정)
# from app.api import auth, posts, admin

@api_bp.route('/ping')
def ping():
    """API 연결 테스트 엔드포인트"""
    return {'message': 'pong', 'version': '1.0.0'}, 200
