"""
A/B 테스팅 모델
"""

from app import db
from datetime import datetime
import random


class ABTest(db.Model):
    """A/B 테스트 실험"""
    __tablename__ = 'ab_tests'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True, index=True)
    description = db.Column(db.Text)

    # 상태: draft, running, paused, completed
    status = db.Column(db.String(20), default='draft', index=True)

    # 변형(Variant) 정의
    # {
    #   "control": {"name": "Original", "weight": 50},
    #   "variant_a": {"name": "New Design", "weight": 50}
    # }
    variants = db.Column(db.JSON, nullable=False)

    # 목표 메트릭: click_rate, conversion_rate, engagement_time 등
    goal_metric = db.Column(db.String(50))

    # 타임스탬프
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime)
    ended_at = db.Column(db.DateTime)

    # 관계
    assignments = db.Relationship('ABTestAssignment', backref='test', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<ABTest {self.name} ({self.status})>'

    def assign_variant(self, user_id=None, session_id=None):
        """사용자/세션에 변형 할당"""
        # 이미 할당되어 있는지 확인
        existing = ABTestAssignment.query.filter_by(
            test_id=self.id,
            user_id=user_id,
            session_id=session_id
        ).first()

        if existing:
            return existing.variant

        # 가중치 기반 랜덤 할당
        variants_list = []
        weights = []

        for variant_key, variant_info in self.variants.items():
            variants_list.append(variant_key)
            weights.append(variant_info.get('weight', 50))

        # 가중치 기반 랜덤 선택
        total_weight = sum(weights)
        r = random.uniform(0, total_weight)

        cumulative = 0
        selected_variant = variants_list[0]

        for variant, weight in zip(variants_list, weights):
            cumulative += weight
            if r <= cumulative:
                selected_variant = variant
                break

        # 할당 저장
        assignment = ABTestAssignment(
            test_id=self.id,
            user_id=user_id,
            session_id=session_id,
            variant=selected_variant
        )

        db.session.add(assignment)
        db.session.commit()

        return selected_variant

    def get_variant(self, user_id=None, session_id=None):
        """사용자/세션의 할당된 변형 조회"""
        assignment = ABTestAssignment.query.filter_by(
            test_id=self.id,
            user_id=user_id,
            session_id=session_id
        ).first()

        return assignment.variant if assignment else None

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'status': self.status,
            'variants': self.variants,
            'goal_metric': self.goal_metric,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
        }


class ABTestAssignment(db.Model):
    """A/B 테스트 할당"""
    __tablename__ = 'ab_test_assignments'

    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('ab_tests.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    session_id = db.Column(db.String(100), nullable=True, index=True)

    # 할당된 변형
    variant = db.Column(db.String(50), nullable=False)

    # 타임스탬프
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # 관계
    user = db.Relationship('User', backref='ab_test_assignments')
    events = db.Relationship('ABTestEvent', backref='assignment', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<ABTestAssignment test={self.test_id} variant={self.variant}>'


class ABTestEvent(db.Model):
    """A/B 테스트 이벤트"""
    __tablename__ = 'ab_test_events'

    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('ab_test_assignments.id'), nullable=False, index=True)

    # 이벤트 타입: view, click, conversion, etc.
    event_type = db.Column(db.String(50), nullable=False, index=True)

    # 이벤트 값 (선택적)
    value = db.Column(db.Float)

    # 추가 데이터
    metadata = db.Column(db.JSON)

    # 타임스탬프
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f'<ABTestEvent {self.event_type} for assignment {self.assignment_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'assignment_id': self.assignment_id,
            'event_type': self.event_type,
            'value': self.value,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
        }
