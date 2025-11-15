"""
User 모델
관리자 및 작성자 계정 관리
"""
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models.base import BaseModel


class User(BaseModel):
    """사용자/관리자 모델"""
    __tablename__ = 'users'

    # 기본 정보
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    # 권한
    role = db.Column(
        db.String(20),
        nullable=False,
        default='writer',
        server_default='writer'
    )  # admin, editor, writer

    # 상태
    is_active = db.Column(db.Boolean, nullable=False, default=True, server_default='1')

    # 관계
    posts = db.relationship('Post', back_populates='author', lazy='dynamic')
    drafts = db.relationship('Draft', back_populates='author', lazy='dynamic')

    def __init__(self, **kwargs):
        """
        User 초기화

        Args:
            password: 평문 비밀번호 (해싱됨)
            **kwargs: 기타 필드
        """
        password = kwargs.pop('password', None)
        super().__init__(**kwargs)

        if password:
            self.set_password(password)

    def set_password(self, password):
        """
        비밀번호 해싱 후 저장

        Args:
            password: 평문 비밀번호
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        비밀번호 검증

        Args:
            password: 검증할 평문 비밀번호

        Returns:
            bool: 비밀번호 일치 여부
        """
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        """관리자 권한 확인"""
        return self.role == 'admin'

    def is_editor(self):
        """편집자 권한 확인"""
        return self.role in ['admin', 'editor']

    def to_dict(self, exclude=None):
        """
        딕셔너리 변환 (비밀번호 제외)

        Args:
            exclude: 추가로 제외할 필드

        Returns:
            dict: 사용자 데이터
        """
        exclude = exclude or []
        exclude.append('password_hash')
        data = super().to_dict(exclude=exclude)

        # 추가 정보
        data['post_count'] = self.posts.count()
        data['draft_count'] = self.drafts.count()

        return data

    def __repr__(self):
        return f"<User {self.username}>"


# Validation constraints
db.Index('idx_user_active', User.is_active)
