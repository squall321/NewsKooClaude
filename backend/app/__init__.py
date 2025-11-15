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

    # Import models (for Flask-Migrate)
    with app.app_context():
        from app import models

    # Register error handlers
    from app.utils.errors import register_error_handlers
    register_error_handlers(app)

    # Configure logging
    if not app.debug and not app.testing:
        import logging
        from logging.handlers import RotatingFileHandler
        import os

        if not os.path.exists('logs'):
            os.mkdir('logs')

        file_handler = RotatingFileHandler('logs/newskoo.log', maxBytes=10240000, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('NewsKoo startup')

    # Register blueprints
    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # Health check endpoint
    @app.route('/health')
    def health_check():
        """서버 상태 체크 엔드포인트"""
        return {'status': 'healthy', 'service': 'NewsKoo API'}, 200

    # Initialize scheduler (production only)
    if not app.debug and not app.testing:
        from app.services.scheduler import init_scheduler
        init_scheduler(app)
        app.logger.info('Scheduler initialized')

    return app
