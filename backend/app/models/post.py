"""
Post 모델
발행된 게시물 관리
"""
from datetime import datetime
from app import db
from app.models.base import BaseModel
from app.models.tag import post_tags
from slugify import slugify


class Post(BaseModel):
    """게시물 모델"""
    __tablename__ = 'posts'

    # 작성자
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    # 카테고리
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False, index=True)

    # 초안 관계 (선택적)
    draft_id = db.Column(
        db.Integer,
        db.ForeignKey('drafts.id'),
        nullable=True,
        unique=True,  # 1:1 관계
        index=True
    )

    # 콘텐츠
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)  # Markdown
    content_html = db.Column(db.Text, nullable=True)  # HTML (렌더링된 버전)

    # URL
    slug = db.Column(db.String(250), unique=True, nullable=False, index=True)

    # 썸네일 (선택적)
    thumbnail_url = db.Column(db.String(500), nullable=True)

    # 통계
    view_count = db.Column(db.Integer, nullable=False, default=0, server_default='0')

    # 발행 상태
    is_published = db.Column(db.Boolean, nullable=False, default=False, server_default='0', index=True)
    published_at = db.Column(db.DateTime, nullable=True, index=True)

    # 관계
    author = db.relationship('User', back_populates='posts')
    category = db.relationship('Category', back_populates='posts')
    draft = db.relationship('Draft', back_populates='post')
    tags = db.relationship('Tag', secondary=post_tags, backref=db.backref('posts', lazy='dynamic'))

    def __init__(self, **kwargs):
        """
        Post 초기화 (slug 자동 생성)

        Args:
            **kwargs: 필드 값
        """
        # slug가 없으면 title로부터 자동 생성
        if 'slug' not in kwargs and 'title' in kwargs:
            kwargs['slug'] = self._generate_unique_slug(kwargs['title'])

        super().__init__(**kwargs)

    @classmethod
    def _generate_unique_slug(cls, title, instance_id=None):
        """
        고유한 slug 생성

        Args:
            title: 게시물 제목
            instance_id: 업데이트 시 현재 인스턴스 ID

        Returns:
            str: 고유한 slug
        """
        base_slug = slugify(title, max_length=200)
        slug = base_slug
        counter = 1

        while True:
            query = cls.query.filter_by(slug=slug)
            if instance_id:
                query = query.filter(cls.id != instance_id)

            if not query.first():
                return slug

            slug = f"{base_slug}-{counter}"
            counter += 1

    def publish(self):
        """게시물 발행"""
        if not self.is_published:
            self.is_published = True
            self.published_at = datetime.utcnow()
            db.session.commit()

            # 카테고리 게시물 수 업데이트
            if self.category:
                self.category.update_post_count()

            return True
        return False

    def unpublish(self):
        """게시물 숨기기"""
        if self.is_published:
            self.is_published = False
            db.session.commit()

            # 카테고리 게시물 수 업데이트
            if self.category:
                self.category.update_post_count()

            return True
        return False

    def increment_view_count(self):
        """조회수 증가 (비동기 처리 권장)"""
        self.view_count += 1
        db.session.commit()

    def add_tag(self, tag):
        """태그 추가"""
        if tag not in self.tags:
            self.tags.append(tag)
            db.session.commit()

    def remove_tag(self, tag):
        """태그 제거"""
        if tag in self.tags:
            self.tags.remove(tag)
            db.session.commit()

    def set_tags(self, tag_names):
        """
        태그 일괄 설정

        Args:
            tag_names: list of str, 태그 이름 리스트
        """
        from app.models.tag import Tag

        self.tags = []
        for tag_name in tag_names:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            self.tags.append(tag)

        db.session.commit()

    def render_content_html(self):
        """
        Markdown을 HTML로 렌더링
        (향후 markdown2 또는 mistune 라이브러리 사용)
        """
        # Phase 2에서는 간단히 content를 그대로 사용
        # 향후 Phase에서 markdown 렌더링 추가
        self.content_html = self.content
        db.session.commit()

    @classmethod
    def get_published_posts(cls, limit=None, offset=None):
        """
        발행된 게시물 목록

        Args:
            limit: 제한 개수
            offset: 시작 위치

        Returns:
            list: 발행된 게시물 리스트
        """
        query = cls.query.filter_by(is_published=True).order_by(cls.published_at.desc())

        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)

        return query.all()

    @classmethod
    def get_by_slug(cls, slug):
        """
        slug로 게시물 찾기

        Args:
            slug: 게시물 slug

        Returns:
            Post or None
        """
        return cls.query.filter_by(slug=slug, is_published=True).first()

    def to_dict(self, exclude=None, include_content=True):
        """
        딕셔너리 변환

        Args:
            exclude: 제외할 필드
            include_content: 콘텐츠 포함 여부

        Returns:
            dict: 게시물 데이터
        """
        exclude = exclude or []

        if not include_content:
            exclude.extend(['content', 'content_html'])

        data = super().to_dict(exclude=exclude)

        # 작성자 정보
        if self.author:
            data['author'] = {
                'id': self.author.id,
                'username': self.author.username
            }

        # 카테고리 정보
        if self.category:
            data['category'] = {
                'id': self.category.id,
                'name': self.category.name,
                'slug': self.category.slug
            }

        # 태그 정보
        data['tags'] = [
            {'id': tag.id, 'name': tag.name, 'slug': tag.slug}
            for tag in self.tags
        ]

        # 미리보기 (콘텐츠 첫 200자)
        if include_content and self.content:
            data['preview'] = self.content[:200] + '...' if len(self.content) > 200 else self.content

        return data

    def __repr__(self):
        return f"<Post {self.slug}>"


# 인덱스
db.Index('idx_post_published', Post.is_published, Post.published_at.desc())
db.Index('idx_post_user', Post.user_id)
db.Index('idx_post_category', Post.category_id)
db.Index('idx_post_slug', Post.slug)
