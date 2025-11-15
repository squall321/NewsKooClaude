"""
모델 테스트
"""
import pytest
from app.models import User, Post, Draft, Category, Tag, Source, Inspiration


class TestUser:
    """User 모델 테스트"""

    def test_create_user(self, db_session):
        """사용자 생성 테스트"""
        user = User.create(
            username='newuser',
            email='new@example.com',
            password='password123',
            role='writer'
        )
        db_session.session.commit()

        assert user.id is not None
        assert user.username == 'newuser'
        assert user.email == 'new@example.com'
        assert user.role == 'writer'
        assert user.is_active is True

    def test_password_hashing(self, db_session):
        """비밀번호 해싱 테스트"""
        user = User(username='testuser', email='test@example.com', password='mypassword')
        db_session.session.add(user)
        db_session.session.commit()

        # 비밀번호가 해시되었는지 확인
        assert user.password_hash != 'mypassword'
        # 비밀번호 검증
        assert user.check_password('mypassword') is True
        assert user.check_password('wrongpassword') is False

    def test_user_roles(self, admin_user, sample_user):
        """사용자 권한 테스트"""
        assert admin_user.is_admin() is True
        assert admin_user.is_editor() is True

        assert sample_user.is_admin() is False
        assert sample_user.is_editor() is False

    def test_user_to_dict(self, sample_user):
        """User to_dict 테스트"""
        user_dict = sample_user.to_dict()

        assert 'id' in user_dict
        assert 'username' in user_dict
        assert 'email' in user_dict
        assert 'password_hash' not in user_dict  # 비밀번호는 제외되어야 함


class TestCategory:
    """Category 모델 테스트"""

    def test_create_category(self, db_session):
        """카테고리 생성 테스트"""
        category = Category.create(
            name='일상 유머',
            description='일상적인 유머'
        )
        db_session.session.commit()

        assert category.id is not None
        assert category.name == '일상 유머'
        assert category.slug is not None  # slug 자동 생성

    def test_slug_generation(self, db_session):
        """Slug 자동 생성 테스트"""
        category = Category(name='테스트 카테고리')
        db_session.session.add(category)
        db_session.session.commit()

        assert category.slug is not None
        assert len(category.slug) > 0


class TestTag:
    """Tag 모델 테스트"""

    def test_create_tag(self, db_session):
        """태그 생성 테스트"""
        tag = Tag.create(name='재미있음')
        db_session.session.commit()

        assert tag.id is not None
        assert tag.name == '재미있음'
        assert tag.slug is not None

    def test_tag_usage_count(self, db_session):
        """태그 사용 횟수 초기값 테스트"""
        tag = Tag.create(name='새태그')
        db_session.session.commit()

        assert tag.usage_count == 0


class TestPost:
    """Post 모델 테스트"""

    def test_create_post(self, db_session, sample_user, sample_category):
        """게시물 생성 테스트"""
        post = Post.create(
            user_id=sample_user.id,
            category_id=sample_category.id,
            title='테스트 게시물',
            content='테스트 콘텐츠입니다.'
        )
        db_session.session.commit()

        assert post.id is not None
        assert post.title == '테스트 게시물'
        assert post.slug is not None
        assert post.is_published is False

    def test_post_publish(self, db_session, sample_user, sample_category):
        """게시물 발행 테스트"""
        post = Post.create(
            user_id=sample_user.id,
            category_id=sample_category.id,
            title='발행 테스트',
            content='내용'
        )
        db_session.session.commit()

        assert post.is_published is False
        assert post.published_at is None

        # 발행
        result = post.publish()

        assert result is True
        assert post.is_published is True
        assert post.published_at is not None

    def test_post_slug_uniqueness(self, db_session, sample_user, sample_category):
        """같은 제목의 게시물 slug 중복 방지 테스트"""
        post1 = Post.create(
            user_id=sample_user.id,
            category_id=sample_category.id,
            title='같은 제목',
            content='내용 1'
        )
        db_session.session.commit()

        post2 = Post.create(
            user_id=sample_user.id,
            category_id=sample_category.id,
            title='같은 제목',
            content='내용 2'
        )
        db_session.session.commit()

        # slug가 다르게 생성되어야 함
        assert post1.slug != post2.slug

    def test_post_tags(self, db_session, sample_user, sample_category, sample_tags):
        """게시물 태그 관계 테스트"""
        post = Post.create(
            user_id=sample_user.id,
            category_id=sample_category.id,
            title='태그 테스트',
            content='내용'
        )
        db_session.session.commit()

        # 태그 추가
        post.add_tag(sample_tags[0])
        post.add_tag(sample_tags[1])

        assert len(post.tags) == 2
        assert sample_tags[0] in post.tags
        assert sample_tags[1] in post.tags


class TestDraft:
    """Draft 모델 테스트"""

    def test_create_draft(self, db_session, sample_user):
        """초안 생성 테스트"""
        draft = Draft.create(
            user_id=sample_user.id,
            title='초안 제목',
            content='초안 내용'
        )
        db_session.session.commit()

        assert draft.id is not None
        assert draft.status == 'idea'

    def test_draft_status_transitions(self, db_session, sample_user):
        """초안 상태 전환 테스트"""
        draft = Draft.create(
            user_id=sample_user.id,
            title='상태 테스트',
            content='내용'
        )
        db_session.session.commit()

        # idea -> writing
        draft.start_writing()
        assert draft.status == 'writing'

        # writing -> ai_assisted
        result = draft.request_ai_assistance()
        assert result is True
        assert draft.status == 'ai_assisted'

        # ai_assisted -> review
        result = draft.submit_for_review()
        assert result is True
        assert draft.status == 'review'

        # review -> completed
        result = draft.complete()
        assert result is True
        assert draft.status == 'completed'


class TestSource:
    """Source 모델 테스트"""

    def test_create_source(self, db_session):
        """소스 생성 테스트"""
        source = Source.create(
            platform='reddit',
            source_url='https://reddit.com/r/funny/test',
            source_id='test123',
            title='Test Post'
        )
        db_session.session.commit()

        assert source.id is not None
        assert source.platform == 'reddit'

    def test_find_by_url(self, db_session):
        """URL로 소스 찾기 테스트"""
        url = 'https://reddit.com/r/test/unique'
        source = Source.create(
            platform='reddit',
            source_url=url,
            source_id='unique123'
        )
        db_session.session.commit()

        found = Source.find_by_url(url)
        assert found is not None
        assert found.id == source.id


class TestInspiration:
    """Inspiration 모델 테스트"""

    def test_create_inspiration(self, db_session):
        """영감 생성 테스트"""
        # Source 먼저 생성
        source = Source.create(
            platform='reddit',
            source_url='https://reddit.com/r/test/insp',
            source_id='insp123'
        )
        db_session.session.commit()

        inspiration = Inspiration.create(
            source_id=source.id,
            original_concept='재미있는 컨셉',
            adaptation_notes='재창작 방향',
            similarity_score=0.45
        )
        db_session.session.commit()

        assert inspiration.id is not None
        assert inspiration.status == 'collected'

    def test_fair_use_compliance(self, db_session):
        """Fair Use 준수 여부 테스트"""
        source = Source.create(
            platform='reddit',
            source_url='https://reddit.com/r/test/fair',
            source_id='fair123'
        )
        db_session.session.commit()

        # 유사도 60% (준수)
        inspiration1 = Inspiration.create(
            source_id=source.id,
            original_concept='컨셉',
            similarity_score=0.6
        )
        db_session.session.commit()
        assert inspiration1.is_fair_use_compliant is True

        # 유사도 75% (미준수)
        inspiration2 = Inspiration.create(
            source_id=source.id,
            original_concept='컨셉2',
            similarity_score=0.75
        )
        db_session.session.commit()
        assert inspiration2.is_fair_use_compliant is False
