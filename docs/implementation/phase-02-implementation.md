# Phase 2 구현 상세 문서

**Phase**: 데이터베이스 설계 및 모델 정의
**완료 날짜**: 2025-11-15
**소요 시간**: 약 3-4시간

---

## 📋 개요

Phase 2에서는 NewsKoo 플랫폼의 데이터베이스 스키마를 설계하고 SQLAlchemy 모델을 구현했습니다. 재창작 철학을 반영한 8개의 핵심 모델을 정의하고, 관계를 설정했습니다.

---

## 🎯 달성 목표

- ✅ ERD (Entity Relationship Diagram) 설계
- ✅ 8개 핵심 모델 구현
- ✅ Flask-Migrate 설정
- ✅ Seed 데이터 스크립트 작성
- ✅ 모델 테스트 작성

---

## 📊 ERD 설계

### 핵심 엔티티 (8개)

1. **User** - 사용자/관리자
2. **Post** - 발행된 게시물
3. **Draft** - 작성 중인 초안
4. **Category** - 카테고리
5. **Tag** - 태그
6. **Source** - 외부 소스 (메타데이터)
7. **Inspiration** - 영감/재창작 아이디어
8. **WritingStyle** - AI 프롬프트 템플릿

### 관계 설계

```
User 1:N Post (작성자)
User 1:N Draft

Category 1:N Post
Post N:N Tag (중간 테이블: post_tags)

Source 1:N Inspiration
Inspiration 1:1 Draft (선택적)
Draft 1:1 Post (선택적)

WritingStyle 1:N Draft
```

**문서**: [DATABASE_ERD.md](../DATABASE_ERD.md)

---

## 🔧 구현 내용

### 1. Base Model 및 Mixin

**파일**: `backend/app/models/base.py`

```python
class TimestampMixin:
    """모든 모델에 created_at, updated_at 자동 추가"""
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class BaseModel(db.Model, TimestampMixin):
    """공통 기능 제공"""
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)

    def to_dict(self, exclude=None):
        """모델을 딕셔너리로 변환"""

    def save(self):
        """모델 저장"""

    def delete(self):
        """모델 삭제"""
```

**주요 기능**:
- 자동 타임스탬프 관리
- `to_dict()` - JSON 직렬화
- `save()`, `delete()` - CRUD 헬퍼
- `create()` - 클래스 메서드로 인스턴스 생성

---

### 2. User 모델

**파일**: `backend/app/models/user.py`

**주요 필드**:
- `username` (unique)
- `email` (unique)
- `password_hash` (Werkzeug로 해싱)
- `role` (admin, editor, writer)
- `is_active`

**주요 메서드**:
- `set_password()` - 비밀번호 해싱
- `check_password()` - 비밀번호 검증
- `is_admin()`, `is_editor()` - 권한 확인

**관계**:
- `posts` (1:N)
- `drafts` (1:N)

---

### 3. Category 모델

**파일**: `backend/app/models/category.py`

**주요 필드**:
- `name` (unique) - 카테고리 이름
- `slug` (unique, 자동 생성) - URL slug
- `description`
- `post_count` - 게시물 수 (캐싱)

**주요 메서드**:
- `__init__()` - slug 자동 생성 (python-slugify)
- `update_post_count()` - 게시물 수 업데이트

---

### 4. Tag 모델

**파일**: `backend/app/models/tag.py`

**주요 필드**:
- `name` (unique)
- `slug` (unique, 자동 생성)
- `usage_count` - 사용 횟수

**중간 테이블**:
- `post_tags` - Post와 Tag의 N:N 관계

---

### 5. Source 모델

**파일**: `backend/app/models/source.py`

**저작권 준수**: 전체 콘텐츠를 저장하지 않고 **메타데이터만 저장**

**주요 필드**:
- `platform` (reddit, other)
- `source_url` (unique) - 원본 URL
- `source_id` - 플랫폼별 ID
- `title`, `author`, `score`
- `posted_at` - 원본 게시 시각
- `metadata_json` - 추가 메타데이터 (JSON)

**주요 메서드**:
- `find_by_url()` - URL로 검색
- `create_from_reddit()` - Reddit 데이터로부터 생성

---

### 6. Inspiration 모델

**파일**: `backend/app/models/inspiration.py`

**재창작 아이디어 관리**

**주요 필드**:
- `source_id` (FK to Source)
- `original_concept` - 원본에서 추출한 핵심 컨셉
- `adaptation_notes` - 재창작 방향 노트
- `similarity_score` (0.0 ~ 1.0) - **Fair Use 판단용**
- `status` (collected, reviewing, approved, in_progress, completed, rejected)

**주요 메서드**:
- `is_fair_use_compliant` - 유사도 70% 미만 확인
- `approve()`, `reject()` - 승인/거절
- `start_writing()`, `complete()` - 상태 전환

---

### 7. WritingStyle 모델

**파일**: `backend/app/models/writing_style.py`

**AI 프롬프트 템플릿 관리**

**주요 필드**:
- `name` (unique)
- `prompt_template` - 프롬프트 템플릿 (Python format 문자열)
- `system_message` - AI 시스템 메시지
- `example_output` - 예시 출력
- `is_active` - 활성화 여부

**주요 메서드**:
- `generate_prompt(context_data)` - 컨텍스트로 프롬프트 생성
- `get_active_styles()` - 활성화된 스타일 목록
- `get_default_style()` - 기본 스타일

---

### 8. Draft 모델

**파일**: `backend/app/models/draft.py`

**작성 중인 콘텐츠 관리**

**주요 필드**:
- `user_id` (FK to User)
- `inspiration_id` (FK to Inspiration, 선택적)
- `writing_style_id` (FK to WritingStyle, 선택적)
- `title`, `content`
- `ai_suggestions` - AI 제안 (선택적)
- `status` (idea, writing, ai_assisted, review, completed, abandoned)

**주요 메서드**:
- `start_writing()` - 작성 시작
- `request_ai_assistance()` - AI 보조 요청
- `submit_for_review()` - 검토 제출
- `complete()` - 완료
- `abandon()` - 중단

---

### 9. Post 모델

**파일**: `backend/app/models/post.py`

**발행된 게시물**

**주요 필드**:
- `user_id` (FK to User)
- `category_id` (FK to Category)
- `draft_id` (FK to Draft, 선택적)
- `title`, `content` (Markdown)
- `content_html` (렌더링된 HTML)
- `slug` (unique, 자동 생성)
- `thumbnail_url`
- `view_count`
- `is_published`, `published_at`

**주요 메서드**:
- `publish()`, `unpublish()` - 발행/숨기기
- `increment_view_count()` - 조회수 증가
- `add_tag()`, `remove_tag()`, `set_tags()` - 태그 관리
- `get_published_posts()` - 발행된 게시물 목록
- `get_by_slug()` - slug로 검색

**Slug 중복 방지**:
- 같은 제목이 있을 경우 `title-1`, `title-2` 등으로 자동 생성

---

## 📦 생성된 파일

### 모델 파일

```
backend/app/models/
├── __init__.py          # 모든 모델 export
├── base.py              # BaseModel, TimestampMixin
├── user.py              # User 모델
├── category.py          # Category 모델
├── tag.py               # Tag 모델, post_tags 중간 테이블
├── source.py            # Source 모델
├── inspiration.py       # Inspiration 모델
├── writing_style.py     # WritingStyle 모델
├── draft.py             # Draft 모델
└── post.py              # Post 모델
```

### 스크립트 및 테스트

```
backend/
├── scripts/
│   └── seed_data.py     # Seed 데이터 생성 스크립트
└── tests/
    ├── __init__.py
    ├── conftest.py      # pytest fixtures
    └── test_models.py   # 모델 테스트
```

### 문서

```
docs/
├── DATABASE_ERD.md      # ERD 다이어그램 및 설계 문서
└── implementation/
    └── phase-02-implementation.md  # 이 문서
```

---

## 🔑 핵심 설계 결정

### 1. Fair Use 준수

**문제**: Reddit 콘텐츠 사용 시 저작권 이슈

**해결**:
- Source 모델은 **메타데이터만 저장** (URL, 제목, 작성자)
- Inspiration 모델에서 `similarity_score` 관리
- 70% 미만 유사도 권장 (`is_fair_use_compliant`)

### 2. 워크플로우 설계

**창작 프로세스**:
```
Source (수집)
  → Inspiration (영감, 검토)
    → Draft (초안 작성)
      → Post (발행)
```

각 단계별로 독립적인 모델로 분리하여 **작업 흐름 추적** 가능

### 3. Slug 자동 생성

**문제**: 게시물 URL이 중복될 수 있음

**해결**:
- `python-slugify` 라이브러리 사용
- 중복 시 자동으로 `-1`, `-2` 추가
- Category, Tag도 동일한 방식

### 4. 타임스탬프 자동 관리

**TimestampMixin**:
- `created_at` - 생성 시각 (자동)
- `updated_at` - 수정 시각 (자동 갱신)

모든 모델에 일관되게 적용

### 5. 유연한 상태 관리

**Draft.status**:
- `idea` → `writing` → `ai_assisted` → `review` → `completed`
- 각 상태 전환 메서드 제공

**Inspiration.status**:
- `collected` → `reviewing` → `approved` → `in_progress` → `completed`

---

## ✅ 검증

### Seed 데이터 스크립트

**실행 방법** (Phase 3에서 진행 예정):
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python scripts/seed_data.py
```

**생성되는 데이터**:
- 3명의 사용자 (admin, editor, writer)
- 6개 카테고리
- 16개 태그
- 3개 작성 스타일
- 1개 샘플 Source
- 1개 샘플 Inspiration
- 1개 샘플 Draft
- 1개 샘플 Post (발행됨)

**기본 로그인**:
- Username: `admin`
- Password: `admin123` (프로덕션에서 변경 필요)

### 테스트

**실행 방법** (Phase 3에서 진행 예정):
```bash
pytest tests/ -v
pytest tests/ --cov=app
```

**테스트 커버리지**:
- User 모델: 비밀번호 해싱, 권한, to_dict
- Category: slug 생성
- Tag: 생성 및 usage_count
- Post: 생성, 발행, slug 중복 방지, 태그 관계
- Draft: 상태 전환
- Source: URL 검색
- Inspiration: Fair Use 준수 여부

---

## 📊 통계

- **생성된 모델**: 8개
- **모델 파일**: 9개 (base 포함)
- **코드 라인**: 약 1,500줄
- **테스트 케이스**: 20+개
- **Seed 데이터 스크립트**: 약 300줄

---

## 💡 배운 점

1. **SQLAlchemy 관계 설정**: `back_populates`와 `backref`의 차이
2. **Mixin 패턴**: 공통 기능을 Mixin으로 분리하여 재사용
3. **Slug 생성**: 중복 방지 로직 구현
4. **Fair Use 설계**: 유사도 점수로 저작권 준수
5. **상태 관리**: Enum 대신 문자열 + 메서드로 상태 전환

---

## ⚠️ 주의사항

### Migration 미실행

Phase 2에서는 모델 정의만 완료했고, **실제 Migration은 Phase 3에서 진행**합니다.

이유:
- 개발 환경에서 Python 패키지 설치 후 진행 필요
- `flask db init`, `flask db migrate`, `flask db upgrade` 순서로 실행

### 비밀번호 보안

Seed 데이터의 기본 비밀번호는 개발용입니다. **프로덕션 환경에서는 반드시 변경**해야 합니다.

### Markdown 렌더링

Post 모델의 `render_content_html()` 메서드는 현재 미구현 상태입니다. Phase 후반에 `markdown2` 또는 `mistune` 라이브러리를 사용하여 구현 예정입니다.

---

## 🔄 다음 단계 (Phase 3)

**Phase 3: Flask API 기본 구조**

주요 작업:
1. Flask-Migrate 초기화 및 Migration 생성
2. REST API 엔드포인트 구현
3. Request/Response 검증 (Pydantic)
4. 에러 핸들링
5. API 문서화 (Swagger/OpenAPI)

---

**Phase 2 완료 ✅**

다음: [Phase 3 - Flask API 기본 구조](./phase-03-implementation.md)
