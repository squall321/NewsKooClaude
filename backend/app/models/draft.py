"""
Draft 모델
작성 중인 콘텐츠 관리 (AI 보조 또는 수동 작성)
"""
from app import db
from app.models.base import BaseModel


class Draft(BaseModel):
    """초안 모델"""
    __tablename__ = 'drafts'

    # 작성자
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    # 영감 관계 (선택적)
    inspiration_id = db.Column(
        db.Integer,
        db.ForeignKey('inspirations.id'),
        nullable=True,
        unique=True,  # 1:1 관계
        index=True
    )

    # 작성 스타일 (선택적)
    writing_style_id = db.Column(
        db.Integer,
        db.ForeignKey('writing_styles.id'),
        nullable=True,
        index=True
    )

    # 콘텐츠
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)

    # AI 보조 제안 (선택적)
    ai_suggestions = db.Column(db.Text, nullable=True)

    # 상태
    status = db.Column(
        db.String(20),
        nullable=False,
        default='idea',
        server_default='idea',
        index=True
    )  # idea, writing, ai_assisted, review, completed, abandoned

    # 관계
    author = db.relationship('User', back_populates='drafts')
    inspiration = db.relationship('Inspiration', back_populates='draft')
    writing_style = db.relationship('WritingStyle', back_populates='drafts')
    post = db.relationship('Post', back_populates='draft', uselist=False)  # 1:1

    @property
    def status_display(self):
        """상태 표시명"""
        status_names = {
            'idea': '아이디어',
            'writing': '작성 중',
            'ai_assisted': 'AI 보조 중',
            'review': '검토 중',
            'completed': '완료',
            'abandoned': '중단'
        }
        return status_names.get(self.status, self.status)

    @property
    def is_completed(self):
        """완료 여부"""
        return self.status == 'completed'

    @property
    def is_published(self):
        """발행 여부"""
        return self.post is not None and self.post.is_published

    def start_writing(self):
        """작성 시작"""
        if self.status == 'idea':
            self.status = 'writing'
            db.session.commit()

    def request_ai_assistance(self):
        """AI 보조 요청"""
        if self.status in ['idea', 'writing']:
            self.status = 'ai_assisted'
            db.session.commit()
            return True
        return False

    def submit_for_review(self):
        """검토 제출"""
        if self.status in ['writing', 'ai_assisted']:
            self.status = 'review'
            db.session.commit()
            return True
        return False

    def complete(self):
        """완료"""
        if self.status == 'review':
            self.status = 'completed'
            db.session.commit()
            return True
        return False

    def abandon(self):
        """중단"""
        self.status = 'abandoned'
        db.session.commit()

    def to_dict(self, exclude=None):
        """딕셔너리 변환"""
        data = super().to_dict(exclude=exclude)

        # 추가 정보
        data['status_display'] = self.status_display
        data['is_completed'] = self.is_completed
        data['is_published'] = self.is_published

        # 작성자 정보
        if self.author:
            data['author'] = {
                'id': self.author.id,
                'username': self.author.username
            }

        # Inspiration 정보
        if self.inspiration:
            data['inspiration'] = {
                'id': self.inspiration.id,
                'original_concept': self.inspiration.original_concept[:100] + '...'
                if len(self.inspiration.original_concept) > 100
                else self.inspiration.original_concept
            }

        # WritingStyle 정보
        if self.writing_style:
            data['writing_style'] = {
                'id': self.writing_style.id,
                'name': self.writing_style.name
            }

        return data

    def __repr__(self):
        return f"<Draft {self.id}: {self.title[:30]}>"


# 인덱스
db.Index('idx_draft_status', Draft.status)
db.Index('idx_draft_user', Draft.user_id)
db.Index('idx_draft_inspiration', Draft.inspiration_id)
