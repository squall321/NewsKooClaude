"""
API 통합 테스트
"""
import pytest
from app.models import User, Category, Tag, Post


class TestPostsAPI:
    """Posts API 테스트"""

    def test_get_posts(self, client, db_session, sample_user, sample_category):
        """게시물 목록 조회 테스트"""
        # 테스트 게시물 생성
        post = Post.create(
            user_id=sample_user.id,
            category_id=sample_category.id,
            title='테스트 게시물',
            content='내용',
            is_published=True
        )
        post.publish()
        db_session.session.commit()

        # API 호출
        response = client.get('/api/posts')

        assert response.status_code == 200
        data = response.get_json()
        assert 'posts' in data
        assert 'pagination' in data
        assert len(data['posts']) >= 1

    def test_get_post_detail(self, client, db_session, sample_user, sample_category):
        """게시물 상세 조회 테스트"""
        # 테스트 게시물 생성
        post = Post.create(
            user_id=sample_user.id,
            category_id=sample_category.id,
            title='상세 조회 테스트',
            content='내용',
            is_published=True
        )
        post.publish()
        db_session.session.commit()

        # API 호출
        response = client.get(f'/api/posts/{post.id}')

        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == post.id
        assert data['title'] == '상세 조회 테스트'

    def test_get_post_by_slug(self, client, db_session, sample_user, sample_category):
        """Slug로 게시물 조회 테스트"""
        # 테스트 게시물 생성
        post = Post.create(
            user_id=sample_user.id,
            category_id=sample_category.id,
            title='Slug 테스트',
            content='내용',
            is_published=True
        )
        post.publish()
        db_session.session.commit()

        # API 호출
        response = client.get(f'/api/posts/slug/{post.slug}')

        assert response.status_code == 200
        data = response.get_json()
        assert data['slug'] == post.slug

    def test_get_post_not_found(self, client):
        """존재하지 않는 게시물 조회 테스트"""
        response = client.get('/api/posts/99999')

        assert response.status_code == 404
        data = response.get_json()
        assert data['error'] is True


class TestCategoriesAPI:
    """Categories API 테스트"""

    def test_get_categories(self, client, db_session, sample_category):
        """카테고리 목록 조회 테스트"""
        response = client.get('/api/categories')

        assert response.status_code == 200
        data = response.get_json()
        assert 'categories' in data
        assert len(data['categories']) >= 1

    def test_get_category_detail(self, client, sample_category):
        """카테고리 상세 조회 테스트"""
        response = client.get(f'/api/categories/{sample_category.id}')

        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == sample_category.id
        assert data['name'] == sample_category.name

    def test_get_category_by_slug(self, client, sample_category):
        """Slug로 카테고리 조회 테스트"""
        response = client.get(f'/api/categories/slug/{sample_category.slug}')

        assert response.status_code == 200
        data = response.get_json()
        assert data['slug'] == sample_category.slug

    def test_get_category_not_found(self, client):
        """존재하지 않는 카테고리 조회 테스트"""
        response = client.get('/api/categories/99999')

        assert response.status_code == 404
        data = response.get_json()
        assert data['error'] is True


class TestTagsAPI:
    """Tags API 테스트"""

    def test_get_tags(self, client, db_session, sample_tags):
        """태그 목록 조회 테스트"""
        response = client.get('/api/tags')

        assert response.status_code == 200
        data = response.get_json()
        assert 'tags' in data
        assert len(data['tags']) >= 3

    def test_get_tag_detail(self, client, sample_tags):
        """태그 상세 조회 테스트"""
        tag = sample_tags[0]
        response = client.get(f'/api/tags/{tag.id}')

        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == tag.id
        assert data['name'] == tag.name

    def test_get_tag_by_slug(self, client, sample_tags):
        """Slug로 태그 조회 테스트"""
        tag = sample_tags[0]
        response = client.get(f'/api/tags/slug/{tag.slug}')

        assert response.status_code == 200
        data = response.get_json()
        assert data['slug'] == tag.slug

    def test_get_tags_sorted_by_usage(self, client, sample_tags):
        """사용 횟수로 정렬된 태그 목록 테스트"""
        response = client.get('/api/tags?sort=usage_count')

        assert response.status_code == 200
        data = response.get_json()
        assert 'tags' in data


class TestAPIErrors:
    """API 에러 핸들링 테스트"""

    def test_404_error(self, client):
        """404 에러 테스트"""
        response = client.get('/api/nonexistent')

        assert response.status_code == 404
        data = response.get_json()
        assert data['error'] is True
        assert 'message' in data

    def test_ping_endpoint(self, client):
        """Ping 엔드포인트 테스트"""
        response = client.get('/api/ping')

        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'pong'
        assert data['version'] == '1.0.0'

    def test_health_check(self, client):
        """Health check 엔드포인트 테스트"""
        response = client.get('/health')

        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert data['service'] == 'NewsKoo API'
