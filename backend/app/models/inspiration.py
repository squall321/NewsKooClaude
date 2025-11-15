"""
Inspiration 모델
Source로부터 영감을 받은 재창작 아이디어
"""
from app import db
from app.models.base import BaseModel


class Inspiration(BaseModel):
    """영감 모델"""
    __tablename__ = 'inspirations'

    # 소스 관계
    source_id = db.Column(db.Integer, db.ForeignKey('sources.id'), nullable=False, index=True)

    # 재창작 아이디어
    original_concept = db.Column(db.Text, nullable=False)  # 원본에서 추출한 핵심 컨셉
    adaptation_notes = db.Column(db.Text, nullable=True)  # 재창작 방향 노트

    # 유사도 점수 (원본과의 유사도, Fair Use 판단)
    similarity_score = db.Column(db.Float, nullable=True)  # 0.0 ~ 1.0, 70% 미만 권장

    # 상태
    status = db.Column(
        db.String(20),
        nullable=False,
        default='collected',
        server_default='collected',
        index=True
    )  # collected, reviewing, approved, in_progress, completed, rejected

    # 관계
    source = db.relationship('Source', back_populates='inspirations')
    draft = db.relationship('Draft', back_populates='inspiration', uselist=False)  # 1:1

    @property
    def status_display(self):
        """상태 표시명"""
        status_names = {
            'collected': '수집됨',
            'reviewing': '검토 중',
            'approved': '승인됨',
            'in_progress': '작업 중',
            'completed': '완료됨',
            'rejected': '거절됨'
        }
        return status_names.get(self.status, self.status)

    @property
    def is_fair_use_compliant(self):
        """
        Fair Use 준수 여부
        (유사도 70% 미만)
        """
        if self.similarity_score is None:
            return None
        return self.similarity_score < 0.7

    def approve(self):
        """승인"""
        self.status = 'approved'
        db.session.commit()

    def reject(self):
        """거절"""
        self.status = 'rejected'
        db.session.commit()

    def start_writing(self):
        """작업 시작"""
        if self.status == 'approved':
            self.status = 'in_progress'
            db.session.commit()
            return True
        return False

    def complete(self):
        """작업 완료"""
        self.status = 'completed'
        db.session.commit()

    def to_dict(self, exclude=None):
        """딕셔너리 변환"""
        data = super().to_dict(exclude=exclude)

        # 추가 정보
        data['status_display'] = self.status_display
        data['is_fair_use_compliant'] = self.is_fair_use_compliant
        data['has_draft'] = self.draft is not None

        # Source 정보 포함
        if self.source:
            data['source'] = {
                'id': self.source.id,
                'platform': self.source.platform,
                'title': self.source.title,
                'url': self.source.source_url
            }

        return data

    def __repr__(self):
        return f"<Inspiration {self.id} ({self.status})>"


# 인덱스
db.Index('idx_inspiration_status', Inspiration.status)
db.Index('idx_inspiration_source', Inspiration.source_id)
db.Index('idx_inspiration_similarity', Inspiration.similarity_score)
