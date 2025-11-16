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
from app.api.ai_assistant import ai_assistant_bp
from app.api.inspirations import inspirations_bp
from app.api.sources import sources_bp
from app.api.writing_styles import writing_styles_bp
from app.api.analytics import analytics_bp
from app.api.users import users_bp
from app.api.search import search_bp
from app.api.tracking import tracking_bp
from app.api.ab_test import ab_test_bp

api_bp.register_blueprint(auth_bp, url_prefix='/auth')
api_bp.register_blueprint(posts_bp, url_prefix='/posts')
api_bp.register_blueprint(categories_bp, url_prefix='/categories')
api_bp.register_blueprint(tags_bp, url_prefix='/tags')
api_bp.register_blueprint(admin_bp, url_prefix='/admin')
api_bp.register_blueprint(drafts_bp, url_prefix='/drafts')
api_bp.register_blueprint(ai_assistant_bp, url_prefix='/ai-assistant')
api_bp.register_blueprint(inspirations_bp, url_prefix='/inspirations')
api_bp.register_blueprint(sources_bp, url_prefix='/sources')
api_bp.register_blueprint(writing_styles_bp, url_prefix='/writing-styles')
api_bp.register_blueprint(analytics_bp, url_prefix='/analytics')
api_bp.register_blueprint(users_bp, url_prefix='/users')
api_bp.register_blueprint(search_bp, url_prefix='/search')
api_bp.register_blueprint(tracking_bp, url_prefix='/tracking')
api_bp.register_blueprint(ab_test_bp, url_prefix='/ab-test')
