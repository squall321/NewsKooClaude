"""
Source 모델
외부 소스 (Reddit 등) 메타데이터 저장
저작권 준수: 전체 콘텐츠는 저장하지 않고 URL과 메타데이터만 저장
"""
from datetime import datetime
from app import db
from app.models.base import BaseModel


class Source(BaseModel):
    """외부 소스 모델"""
    __tablename__ = 'sources'

    # 플랫폼 정보
    platform = db.Column(
        db.String(20),
        nullable=False,
        default='reddit',
        server_default='reddit',
        index=True
    )  # reddit, other

    # 소스 정보
    source_url = db.Column(db.String(500), unique=True, nullable=False, index=True)
    source_id = db.Column(db.String(100), nullable=True)  # 플랫폼별 ID (예: Reddit post ID)

    # 메타데이터
    title = db.Column(db.String(300), nullable=True)
    author = db.Column(db.String(100), nullable=True)
    score = db.Column(db.Integer, nullable=True)  # Reddit upvotes 등
    posted_at = db.Column(db.DateTime, nullable=True, index=True)

    # 추가 메타데이터 (JSON)
    metadata_json = db.Column(db.Text, nullable=True)  # subreddit, flair, comments_count 등

    # 관계
    inspirations = db.relationship('Inspiration', back_populates='source', lazy='dynamic')

    @property
    def platform_display(self):
        """플랫폼 표시명"""
        platform_names = {
            'reddit': 'Reddit',
            'other': '기타'
        }
        return platform_names.get(self.platform, self.platform)

    @classmethod
    def find_by_url(cls, url):
        """
        URL로 소스 찾기

        Args:
            url: 소스 URL

        Returns:
            Source or None
        """
        return cls.query.filter_by(source_url=url).first()

    @classmethod
    def create_from_reddit(cls, reddit_post_data):
        """
        Reddit 데이터로부터 Source 생성

        Args:
            reddit_post_data: Reddit API 응답 데이터

        Returns:
            Source: 생성된 소스
        """
        import json

        source = cls(
            platform='reddit',
            source_url=reddit_post_data.get('url'),
            source_id=reddit_post_data.get('id'),
            title=reddit_post_data.get('title'),
            author=reddit_post_data.get('author'),
            score=reddit_post_data.get('score'),
            posted_at=datetime.fromtimestamp(reddit_post_data.get('created_utc', 0)),
            metadata_json=json.dumps({
                'subreddit': reddit_post_data.get('subreddit'),
                'num_comments': reddit_post_data.get('num_comments'),
                'permalink': reddit_post_data.get('permalink'),
            })
        )

        return source

    def to_dict(self, exclude=None):
        """딕셔너리 변환"""
        import json

        data = super().to_dict(exclude=exclude)

        # 메타데이터 파싱
        if self.metadata_json:
            try:
                data['metadata'] = json.loads(self.metadata_json)
            except json.JSONDecodeError:
                data['metadata'] = {}
        else:
            data['metadata'] = {}

        # 추가 정보
        data['platform_display'] = self.platform_display
        data['inspiration_count'] = self.inspirations.count()

        return data

    def __repr__(self):
        return f"<Source {self.platform}:{self.source_id}>"


# 인덱스
db.Index('idx_source_platform', Source.platform)
db.Index('idx_source_posted_at', Source.posted_at.desc())
