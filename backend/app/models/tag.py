"""
Tag 모델
게시물 태그 (N:N 관계)
"""
from app import db
from app.models.base import BaseModel
from slugify import slugify


# Post-Tag 다대다 관계 중간 테이블
post_tags = db.Table(
    'post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True),
    db.Column('created_at', db.DateTime, nullable=False, server_default=db.func.now())
)


class Tag(BaseModel):
    """태그 모델"""
    __tablename__ = 'tags'

    # 기본 정보
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    slug = db.Column(db.String(60), unique=True, nullable=False, index=True)

    # 통계
    usage_count = db.Column(db.Integer, nullable=False, default=0, server_default='0')

    # 관계 (Post 모델에서 정의됨)
    # posts = db.relationship('Post', secondary=post_tags, back_populates='tags')

    def __init__(self, **kwargs):
        """
        Tag 초기화 (slug 자동 생성)

        Args:
            **kwargs: 필드 값
        """
        # slug가 없으면 name으로부터 자동 생성
        if 'slug' not in kwargs and 'name' in kwargs:
            kwargs['slug'] = slugify(kwargs['name'], max_length=60)

        super().__init__(**kwargs)

    def update_usage_count(self):
        """사용 횟수 업데이트"""
        # Post 모델이 정의된 후에만 작동
        from app.models.post import Post
        self.usage_count = db.session.query(post_tags).filter_by(tag_id=self.id).count()
        db.session.commit()

    def to_dict(self, exclude=None):
        """딕셔너리 변환"""
        data = super().to_dict(exclude=exclude)
        return data

    def __repr__(self):
        return f"<Tag {self.name}>"


# 인덱스
db.Index('idx_tag_slug', Tag.slug)
db.Index('idx_tag_usage', Tag.usage_count.desc())
