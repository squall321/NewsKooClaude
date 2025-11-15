"""
애플리케이션 설정 모듈
환경별 설정 관리 (development, production, testing)
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """기본 설정 클래스"""

    # Application
    APP_NAME: str = "NewsKoo"
    DEBUG: bool = False
    TESTING: bool = False
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Database
    SQLALCHEMY_DATABASE_URI: str = 'sqlite:///newskoo.db'
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    # JWT
    JWT_SECRET_KEY: str = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES: int = 3600  # 1 hour

    # CORS
    CORS_ORIGINS: list = ['http://localhost:5173', 'http://localhost:3000']

    # File Upload
    UPLOAD_FOLDER: Path = Path(__file__).parent.parent.parent / 'uploads'
    MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024  # 16MB

    # LLM (Local EEVE-Korean-10.8B on RTX 5070 TI)
    LLM_MODEL_NAME: str = 'yanolja/EEVE-Korean-10.8B-v1.0'
    LLM_DEVICE: str = 'cuda'  # 'cuda' or 'cpu'
    LLM_LOAD_IN_8BIT: bool = True  # INT8 quantization for VRAM savings
    LLM_USE_FLASH_ATTENTION: bool = True  # Flash Attention 2 for speed
    LLM_MAX_INPUT_LENGTH: int = 2048  # Max input tokens
    LLM_MAX_NEW_TOKENS: int = 512  # Max generated tokens
    LLM_TEMPERATURE: float = 0.8  # Sampling temperature (0.0-2.0)
    LLM_TOP_P: float = 0.92  # Nucleus sampling
    LLM_TOP_K: int = 50  # Top-K sampling
    LLM_REPETITION_PENALTY: float = 1.15  # Repetition penalty
    LLM_CACHE_DIR: str = os.getenv('LLM_CACHE_DIR', '')  # Custom cache dir (optional)

    # Reddit API (선택적 - 메타데이터만 크롤링)
    REDDIT_CLIENT_ID: str = os.getenv('REDDIT_CLIENT_ID', '')
    REDDIT_CLIENT_SECRET: str = os.getenv('REDDIT_CLIENT_SECRET', '')
    REDDIT_USER_AGENT: str = 'NewsKoo/1.0'

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


class DevelopmentConfig(Settings):
    """개발 환경 설정"""
    DEBUG: bool = True
    SQLALCHEMY_DATABASE_URI: str = 'sqlite:///newskoo_dev.db'


class ProductionConfig(Settings):
    """프로덕션 환경 설정"""
    DEBUG: bool = False
    SQLALCHEMY_DATABASE_URI: str = os.getenv(
        'DATABASE_URL',
        'postgresql://user:password@localhost/newskoo'
    )
    CORS_ORIGINS: list = [os.getenv('FRONTEND_URL', 'https://newskoo.com')]


class TestingConfig(Settings):
    """테스트 환경 설정"""
    TESTING: bool = True
    SQLALCHEMY_DATABASE_URI: str = 'sqlite:///:memory:'


# 환경별 설정 매핑
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
}
