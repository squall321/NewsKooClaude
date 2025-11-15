"""
WritingStyle 모델
AI 프롬프트 템플릿 및 작성 스타일 관리
"""
from app import db
from app.models.base import BaseModel


class WritingStyle(BaseModel):
    """작성 스타일 모델"""
    __tablename__ = 'writing_styles'

    # 기본 정보
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)

    # 프롬프트 템플릿
    prompt_template = db.Column(db.Text, nullable=False)
    system_message = db.Column(db.Text, nullable=True)
    example_output = db.Column(db.Text, nullable=True)

    # 상태
    is_active = db.Column(db.Boolean, nullable=False, default=True, server_default='1')

    # 관계
    drafts = db.relationship('Draft', back_populates='writing_style', lazy='dynamic')

    @classmethod
    def get_active_styles(cls):
        """
        활성화된 스타일 목록

        Returns:
            list: 활성화된 WritingStyle 리스트
        """
        return cls.query.filter_by(is_active=True).all()

    @classmethod
    def get_default_style(cls):
        """
        기본 스타일 가져오기

        Returns:
            WritingStyle: 기본 스타일 (첫 번째 활성 스타일)
        """
        return cls.query.filter_by(is_active=True).first()

    def generate_prompt(self, context_data):
        """
        컨텍스트 데이터를 사용하여 프롬프트 생성

        Args:
            context_data: dict, 프롬프트 템플릿에 삽입할 데이터

        Returns:
            str: 생성된 프롬프트
        """
        try:
            return self.prompt_template.format(**context_data)
        except KeyError as e:
            raise ValueError(f"Missing required context data: {e}")

    def to_dict(self, exclude=None):
        """딕셔너리 변환"""
        data = super().to_dict(exclude=exclude)

        # 추가 정보
        data['usage_count'] = self.drafts.count()

        return data

    def __repr__(self):
        return f"<WritingStyle {self.name}>"


# 인덱스
db.Index('idx_writing_style_active', WritingStyle.is_active)
