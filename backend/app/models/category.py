"""
Category 모델
게시물 카테고리 (유머 유형 분류)
"""
from app import db
from app.models.base import BaseModel
from slugify import slugify


class Category(BaseModel):
    """카테고리 모델"""
    __tablename__ = 'categories'

    # 기본 정보
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    slug = db.Column(db.String(60), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)

    # 통계
    post_count = db.Column(db.Integer, nullable=False, default=0, server_default='0')

    # 관계
    posts = db.relationship('Post', back_populates='category', lazy='dynamic')

    def __init__(self, **kwargs):
        """
        Category 초기화 (slug 자동 생성)

        Args:
            **kwargs: 필드 값
        """
        # slug가 없으면 name으로부터 자동 생성
        if 'slug' not in kwargs and 'name' in kwargs:
            kwargs['slug'] = slugify(kwargs['name'], max_length=60)

        super().__init__(**kwargs)

    def update_post_count(self):
        """게시물 수 업데이트"""
        self.post_count = self.posts.filter_by(is_published=True).count()
        db.session.commit()

    def to_dict(self, exclude=None):
        """딕셔너리 변환"""
        data = super().to_dict(exclude=exclude)
        # 실시간 게시물 수
        data['active_post_count'] = self.posts.filter_by(is_published=True).count()
        return data

    def __repr__(self):
        return f"<Category {self.name}>"


# 인덱스
db.Index('idx_category_slug', Category.slug)
