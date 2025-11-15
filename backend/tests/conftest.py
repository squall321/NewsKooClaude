"""
Pytest 설정 및 Fixture 정의
"""
import pytest
from app import create_app, db
from app.models import User, Category, Tag, WritingStyle


@pytest.fixture(scope='session')
def app():
    """
    Flask 애플리케이션 fixture (세션 범위)
    """
    app = create_app('testing')
    return app


@pytest.fixture(scope='function')
def client(app):
    """
    Flask 테스트 클라이언트 fixture
    """
    return app.test_client()


@pytest.fixture(scope='function')
def db_session(app):
    """
    데이터베이스 세션 fixture (각 테스트마다 초기화)
    """
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()


@pytest.fixture
def sample_user(db_session):
    """샘플 사용자 fixture"""
    user = User.create(
        username='testuser',
        email='test@example.com',
        password='password123',
        role='writer'
    )
    db_session.session.commit()
    return user


@pytest.fixture
def admin_user(db_session):
    """관리자 사용자 fixture"""
    user = User.create(
        username='admin',
        email='admin@example.com',
        password='admin123',
        role='admin'
    )
    db_session.session.commit()
    return user


@pytest.fixture
def sample_category(db_session):
    """샘플 카테고리 fixture"""
    category = Category.create(
        name='테스트 카테고리',
        description='테스트용 카테고리입니다'
    )
    db_session.session.commit()
    return category


@pytest.fixture
def sample_tags(db_session):
    """샘플 태그들 fixture"""
    tags = []
    for i in range(3):
        tag = Tag.create(name=f'태그{i+1}')
        tags.append(tag)
    db_session.session.commit()
    return tags


@pytest.fixture
def sample_writing_style(db_session):
    """샘플 작성 스타일 fixture"""
    style = WritingStyle.create(
        name='테스트 스타일',
        prompt_template='컨셉: {concept}',
        system_message='테스트용 시스템 메시지'
    )
    db_session.session.commit()
    return style
