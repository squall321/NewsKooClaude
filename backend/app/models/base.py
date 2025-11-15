"""
Base 모델 및 Mixin 클래스
모든 모델이 상속받는 공통 기능
"""
from datetime import datetime
from app import db


class TimestampMixin:
    """타임스탬프 자동 관리 Mixin"""
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


class BaseModel(db.Model, TimestampMixin):
    """모든 모델의 베이스 클래스"""
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)

    def to_dict(self, exclude=None):
        """
        모델을 딕셔너리로 변환

        Args:
            exclude: 제외할 필드 리스트

        Returns:
            dict: 모델 데이터
        """
        exclude = exclude or []
        data = {}

        for column in self.__table__.columns:
            if column.name not in exclude:
                value = getattr(self, column.name)
                # datetime을 ISO 형식으로 변환
                if isinstance(value, datetime):
                    value = value.isoformat()
                data[column.name] = value

        return data

    def update(self, **kwargs):
        """
        모델 업데이트

        Args:
            **kwargs: 업데이트할 필드와 값
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    @classmethod
    def create(cls, **kwargs):
        """
        모델 생성 헬퍼 메서드

        Args:
            **kwargs: 모델 필드와 값

        Returns:
            instance: 생성된 모델 인스턴스
        """
        instance = cls(**kwargs)
        db.session.add(instance)
        return instance

    def save(self):
        """모델 저장"""
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        """모델 삭제"""
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.id}>"
