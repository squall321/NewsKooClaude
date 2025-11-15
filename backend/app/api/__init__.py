"""
API Blueprint
모든 API 라우트를 관리하는 메인 블루프린트
"""
from flask import Blueprint

api_bp = Blueprint('api', __name__)

# Health check
@api_bp.route('/ping')
def ping():
    """API 연결 테스트 엔드포인트"""
    return {'message': 'pong', 'version': '1.0.0'}, 200

# Import and register sub-blueprints
from app.api.auth import auth_bp
from app.api.posts import posts_bp
from app.api.categories import categories_bp
from app.api.tags import tags_bp
from app.api.admin import admin_bp
from app.api.drafts import drafts_bp

api_bp.register_blueprint(auth_bp, url_prefix='/auth')
api_bp.register_blueprint(posts_bp, url_prefix='/posts')
api_bp.register_blueprint(categories_bp, url_prefix='/categories')
api_bp.register_blueprint(tags_bp, url_prefix='/tags')
api_bp.register_blueprint(admin_bp, url_prefix='/admin')
api_bp.register_blueprint(drafts_bp, url_prefix='/drafts')
