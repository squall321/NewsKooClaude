"""
사용자 활동 추적 모델
"""

from app import db
from datetime import datetime


class UserActivity(db.Model):
    """사용자 활동 로그"""
    __tablename__ = 'user_activities'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # 비로그인 사용자는 NULL
    session_id = db.Column(db.String(100), nullable=False, index=True)  # 세션 ID
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(500))

    # 활동 정보
    activity_type = db.Column(db.String(50), nullable=False, index=True)  # view, click, search, like, comment, share
    resource_type = db.Column(db.String(50))  # post, category, tag, user
    resource_id = db.Column(db.Integer)
    action_detail = db.Column(db.JSON)  # 추가 세부 정보

    # 참조 URL (이전 페이지)
    referrer = db.Column(db.String(500))

    # 타임스탬프
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    # 관계
    user = db.Relationship('User', backref='activities')

    def __repr__(self):
        return f'<UserActivity {self.activity_type} by {self.user_id or self.session_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'activity_type': self.activity_type,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'action_detail': self.action_detail,
            'created_at': self.created_at.isoformat(),
        }


class PageView(db.Model):
    """페이지 조회 추적"""
    __tablename__ = 'page_views'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    session_id = db.Column(db.String(100), nullable=False, index=True)
    ip_address = db.Column(db.String(50))

    # 페이지 정보
    path = db.Column(db.String(500), nullable=False, index=True)
    title = db.Column(db.String(200))
    referrer = db.Column(db.String(500))

    # 체류 시간 (초)
    duration = db.Column(db.Integer)

    # 타임스탬프
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계
    user = db.Relationship('User', backref='page_views')

    def __repr__(self):
        return f'<PageView {self.path} at {self.created_at}>'


class SearchLog(db.Model):
    """검색 로그"""
    __tablename__ = 'search_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    session_id = db.Column(db.String(100), nullable=False, index=True)

    # 검색 정보
    query = db.Column(db.String(200), nullable=False, index=True)
    results_count = db.Column(db.Integer)
    filters = db.Column(db.JSON)  # 적용된 필터

    # 클릭된 결과 (사용자가 선택한 결과)
    clicked_result_id = db.Column(db.Integer)
    clicked_result_position = db.Column(db.Integer)  # 몇 번째 결과를 클릭했는지

    # 타임스탬프
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    # 관계
    user = db.Relationship('User', backref='search_logs')

    def __repr__(self):
        return f'<SearchLog "{self.query}" - {self.results_count} results>'
