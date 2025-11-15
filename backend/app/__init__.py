"""
NewsKoo 백엔드 애플리케이션
유머 콘텐츠 플랫폼 Flask API 서버
"""
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

# Extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app(config_name='development'):
    """
    Flask 애플리케이션 팩토리 함수

    Args:
        config_name: 설정 환경 이름 (development, production, testing)

    Returns:
        Flask: 설정된 Flask 애플리케이션 인스턴스
    """
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(f'app.config.{config_name.capitalize()}Config')

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # CORS 설정
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config.get('CORS_ORIGINS', ['http://localhost:5173']),
            "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
        }
    })

    # Register blueprints
    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # Health check endpoint
    @app.route('/health')
    def health_check():
        """서버 상태 체크 엔드포인트"""
        return {'status': 'healthy', 'service': 'NewsKoo API'}, 200

    return app
