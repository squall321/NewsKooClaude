"""
Authentication API 테스트
"""
import pytest
from flask_jwt_extended import create_access_token, create_refresh_token
from app.models import User


class TestAuthRegister:
    """사용자 등록 테스트"""

    def test_register_success(self, client, db_session, admin_user):
        """관리자가 새 사용자 등록 성공"""
        # 관리자 토큰 생성
        access_token = create_access_token(identity=admin_user.id)

        response = client.post(
            '/api/auth/register',
            json={
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password': 'password123',
                'role': 'writer'
            },
            headers={'Authorization': f'Bearer {access_token}'}
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == 'User created successfully'
        assert data['user']['username'] == 'newuser'
        assert data['user']['role'] == 'writer'

    def test_register_without_auth(self, client):
        """인증 없이 사용자 등록 시도"""
        response = client.post(
            '/api/auth/register',
            json={
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password': 'password123'
            }
        )

        assert response.status_code == 401
        data = response.get_json()
        assert data['error'] is True

    def test_register_non_admin(self, client, db_session, sample_user):
        """비관리자가 사용자 등록 시도"""
        # 일반 사용자 토큰
        access_token = create_access_token(identity=sample_user.id)

        response = client.post(
            '/api/auth/register',
            json={
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password': 'password123'
            },
            headers={'Authorization': f'Bearer {access_token}'}
        )

        assert response.status_code == 403
        data = response.get_json()
        assert data['error'] is True

    def test_register_duplicate_username(self, client, db_session, admin_user, sample_user):
        """중복된 사용자명으로 등록 시도"""
        access_token = create_access_token(identity=admin_user.id)

        response = client.post(
            '/api/auth/register',
            json={
                'username': sample_user.username,
                'email': 'different@example.com',
                'password': 'password123'
            },
            headers={'Authorization': f'Bearer {access_token}'}
        )

        assert response.status_code == 409
        data = response.get_json()
        assert 'already exists' in data['message']

    def test_register_invalid_password(self, client, db_session, admin_user):
        """짧은 비밀번호로 등록 시도"""
        access_token = create_access_token(identity=admin_user.id)

        response = client.post(
            '/api/auth/register',
            json={
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password': 'short'  # 8자 미만
            },
            headers={'Authorization': f'Bearer {access_token}'}
        )

        assert response.status_code == 400
        data = response.get_json()
        assert 'at least 8 characters' in data['message']


class TestAuthLogin:
    """로그인 테스트"""

    def test_login_success(self, client, sample_user):
        """로그인 성공"""
        response = client.post(
            '/api/auth/login',
            json={
                'username': sample_user.username,
                'password': 'password123'  # conftest.py에서 설정한 비밀번호
            }
        )

        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert data['message'] == 'Login successful'
        assert data['user']['username'] == sample_user.username

    def test_login_invalid_username(self, client):
        """존재하지 않는 사용자명으로 로그인"""
        response = client.post(
            '/api/auth/login',
            json={
                'username': 'nonexistent',
                'password': 'password123'
            }
        )

        assert response.status_code == 401
        data = response.get_json()
        assert data['error'] is True
        assert 'Invalid username or password' in data['message']

    def test_login_invalid_password(self, client, sample_user):
        """잘못된 비밀번호로 로그인"""
        response = client.post(
            '/api/auth/login',
            json={
                'username': sample_user.username,
                'password': 'wrongpassword'
            }
        )

        assert response.status_code == 401
        data = response.get_json()
        assert data['error'] is True

    def test_login_missing_fields(self, client):
        """필수 필드 누락"""
        response = client.post(
            '/api/auth/login',
            json={'username': 'testuser'}
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data['error'] is True


class TestAuthRefresh:
    """토큰 갱신 테스트"""

    def test_refresh_token_success(self, client, sample_user):
        """Refresh Token으로 Access Token 갱신"""
        refresh_token = create_refresh_token(identity=sample_user.id)

        response = client.post(
            '/api/auth/refresh',
            headers={'Authorization': f'Bearer {refresh_token}'}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data

    def test_refresh_with_access_token(self, client, sample_user):
        """Access Token으로 갱신 시도 (실패해야 함)"""
        access_token = create_access_token(identity=sample_user.id)

        response = client.post(
            '/api/auth/refresh',
            headers={'Authorization': f'Bearer {access_token}'}
        )

        # Refresh Token이 아니므로 실패
        assert response.status_code == 422

    def test_refresh_without_token(self, client):
        """토큰 없이 갱신 시도"""
        response = client.post('/api/auth/refresh')

        assert response.status_code == 401


class TestAuthMe:
    """현재 사용자 조회 테스트"""

    def test_get_current_user(self, client, sample_user):
        """현재 사용자 정보 조회"""
        access_token = create_access_token(identity=sample_user.id)

        response = client.get(
            '/api/auth/me',
            headers={'Authorization': f'Bearer {access_token}'}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == sample_user.id
        assert data['username'] == sample_user.username

    def test_get_current_user_without_token(self, client):
        """토큰 없이 사용자 정보 조회"""
        response = client.get('/api/auth/me')

        assert response.status_code == 401


class TestAuthLogout:
    """로그아웃 테스트"""

    def test_logout_success(self, client, sample_user):
        """로그아웃 성공"""
        access_token = create_access_token(identity=sample_user.id)

        response = client.post(
            '/api/auth/logout',
            headers={'Authorization': f'Bearer {access_token}'}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Logout successful'


class TestAuthChangePassword:
    """비밀번호 변경 테스트"""

    def test_change_password_success(self, client, db_session, sample_user):
        """비밀번호 변경 성공"""
        access_token = create_access_token(identity=sample_user.id)

        response = client.post(
            '/api/auth/change-password',
            json={
                'old_password': 'password123',
                'new_password': 'newpassword123'
            },
            headers={'Authorization': f'Bearer {access_token}'}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Password changed successfully'

        # 비밀번호가 실제로 변경되었는지 확인
        db_session.session.refresh(sample_user)
        assert sample_user.check_password('newpassword123') is True
        assert sample_user.check_password('password123') is False

    def test_change_password_wrong_old_password(self, client, sample_user):
        """잘못된 현재 비밀번호"""
        access_token = create_access_token(identity=sample_user.id)

        response = client.post(
            '/api/auth/change-password',
            json={
                'old_password': 'wrongpassword',
                'new_password': 'newpassword123'
            },
            headers={'Authorization': f'Bearer {access_token}'}
        )

        assert response.status_code == 401
        data = response.get_json()
        assert 'incorrect' in data['message'].lower()

    def test_change_password_too_short(self, client, sample_user):
        """새 비밀번호가 너무 짧음"""
        access_token = create_access_token(identity=sample_user.id)

        response = client.post(
            '/api/auth/change-password',
            json={
                'old_password': 'password123',
                'new_password': 'short'
            },
            headers={'Authorization': f'Bearer {access_token}'}
        )

        assert response.status_code == 400
        data = response.get_json()
        assert 'at least 8 characters' in data['message']
