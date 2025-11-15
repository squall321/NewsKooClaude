# Phase 3 구현 상세 문서

**Phase**: Flask API 기본 구조
**완료 날짜**: 2025-11-15
**소요 시간**: 약 2-3시간

---

## 📋 개요

Phase 3에서는 RESTful API 아키텍처를 구축하고 Flask Blueprint로 확장 가능한 구조를 만들었습니다. Posts, Categories, Tags에 대한 CRUD API를 구현하고, 전역 에러 핸들링 및 로깅을 설정했습니다.

---

## 🎯 달성 목표

- ✅ 에러 핸들링 유틸리티 구현
- ✅ 인증/권한 데코레이터 구현
- ✅ Posts API (CRUD + 발행/숨기기)
- ✅ Categories API (CRUD)
- ✅ Tags API (CRUD)
- ✅ 전역 에러 핸들러 등록
- ✅ 로깅 설정
- ✅ API 통합 테스트

---

## 🔧 구현 내용

### 1. 에러 핸들링

**파일**: `backend/app/utils/errors.py`

#### 커스텀 예외 클래스

```python
class APIError(Exception):
    """기본 API 에러"""
    status_code = 400

class ValidationError(APIError):
    """데이터 검증 에러 (400)"""
    status_code = 400

class AuthenticationError(APIError):
    """인증 에러 (401)"""
    status_code = 401

class AuthorizationError(APIError):
    """권한 에러 (403)"""
    status_code = 403

class NotFoundError(APIError):
    """리소스 없음 (404)"""
    status_code = 404

class ConflictError(APIError):
    """충돌 에러 (409) - 중복 데이터"""
    status_code = 409
```

#### 전역 에러 핸들러

- `@app.errorhandler(APIError)` - 커스텀 API 에러
- `@app.errorhandler(HTTPException)` - Werkzeug HTTP 예외
- `@app.errorhandler(404)` - 404 Not Found
- `@app.errorhandler(500)` - Internal Server Error
- `@app.errorhandler(Exception)` - 예상치 못한 에러

**JSON 응답 형식**:
```json
{
  "error": true,
  "message": "Error description",
  "status_code": 404
}
```

---

### 2. 인증 데코레이터

**파일**: `backend/app/utils/decorators.py`

#### `@jwt_required_custom`
- JWT 토큰 검증
- 커스텀 에러 메시지

#### `@admin_required`
- 관리자 권한 필요
- User 모델의 `is_admin()` 확인

#### `@editor_required`
- 편집자 이상 권한 필요
- User 모델의 `is_editor()` 확인

#### `get_current_user()`
- 현재 인증된 사용자 가져오기
- 옵셔널 인증 지원

**사용 예시**:
```python
@posts_bp.route('', methods=['POST'])
@jwt_required_custom
@editor_required
def create_post():
    # 편집자 이상만 게시물 작성 가능
    ...
```

---

### 3. Posts API

**파일**: `backend/app/api/posts.py`

#### 엔드포인트

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/posts` | 게시물 목록 | Public |
| GET | `/api/posts/:id` | 게시물 상세 | Public* |
| GET | `/api/posts/slug/:slug` | Slug로 조회 | Public |
| POST | `/api/posts` | 게시물 생성 | Editor+ |
| PUT | `/api/posts/:id` | 게시물 수정 | Editor+ |
| DELETE | `/api/posts/:id` | 게시물 삭제 | Editor+ |
| POST | `/api/posts/:id/publish` | 게시물 발행 | Editor+ |
| POST | `/api/posts/:id/unpublish` | 게시물 숨기기 | Editor+ |

*미발행 게시물은 편집자 이상만 조회 가능

#### 주요 기능

**게시물 목록 (GET /api/posts)**:
- 페이지네이션 (`page`, `per_page`)
- 카테고리 필터 (`category_id`)
- 태그 필터 (`tag`)
- 발행 상태 필터 (`published`)

**응답 예시**:
```json
{
  "posts": [
    {
      "id": 1,
      "title": "게시물 제목",
      "slug": "ge-si-mul-jemog",
      "category": {"id": 1, "name": "일상 유머"},
      "tags": [{"id": 1, "name": "재미있음"}],
      "preview": "내용 미리보기...",
      "view_count": 42,
      "published_at": "2025-11-15T12:00:00",
      "created_at": "2025-11-15T10:00:00"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "pages": 5,
    "has_next": true,
    "has_prev": false
  }
}
```

**게시물 생성 (POST /api/posts)**:
- 필수 필드: `title`, `content`, `category_id`
- 선택 필드: `tags`, `draft_id`, `thumbnail_url`
- 태그 자동 생성/연결
- HTML 렌더링

---

### 4. Categories API

**파일**: `backend/app/api/categories.py`

#### 엔드포인트

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/categories` | 카테고리 목록 | Public |
| GET | `/api/categories/:id` | 카테고리 상세 | Public |
| GET | `/api/categories/slug/:slug` | Slug로 조회 | Public |
| POST | `/api/categories` | 카테고리 생성 | Admin |
| PUT | `/api/categories/:id` | 카테고리 수정 | Admin |
| DELETE | `/api/categories/:id` | 카테고리 삭제 | Admin |

#### 주요 기능

- Slug 자동 생성
- 중복 검증 (이름, slug)
- 게시물 있는 카테고리 삭제 방지

---

### 5. Tags API

**파일**: `backend/app/api/tags.py`

#### 엔드포인트

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/tags` | 태그 목록 | Public |
| GET | `/api/tags/:id` | 태그 상세 | Public |
| GET | `/api/tags/slug/:slug` | Slug로 조회 | Public |
| POST | `/api/tags` | 태그 생성 | Admin |
| PUT | `/api/tags/:id` | 태그 수정 | Admin |
| DELETE | `/api/tags/:id` | 태그 삭제 | Admin |

#### 주요 기능

- 정렬 (`sort=name` 또는 `sort=usage_count`)
- 제한 개수 (`limit`, 최대 500)
- Slug 자동 생성
- 중복 검증

---

### 6. 로깅 설정

**파일**: `backend/app/__init__.py`

#### 설정 내용

- **파일 로거**: `logs/newskoo.log`
- **로테이션**: 10MB마다, 최대 10개 백업 파일
- **로그 레벨**: INFO
- **로그 형식**: `%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]`

**프로덕션 환경에서만 활성화** (debug=False, testing=False)

---

### 7. Blueprint 구조

```
/api
├── /ping                # Health check
├── /posts               # Posts API
│   ├── GET /            # 목록
│   ├── GET /:id         # 상세
│   ├── GET /slug/:slug  # Slug 조회
│   ├── POST /           # 생성
│   ├── PUT /:id         # 수정
│   ├── DELETE /:id      # 삭제
│   ├── POST /:id/publish     # 발행
│   └── POST /:id/unpublish   # 숨기기
├── /categories          # Categories API
│   ├── GET /
│   ├── GET /:id
│   ├── GET /slug/:slug
│   ├── POST /
│   ├── PUT /:id
│   └── DELETE /:id
└── /tags                # Tags API
    ├── GET /
    ├── GET /:id
    ├── GET /slug/:slug
    ├── POST /
    ├── PUT /:id
    └── DELETE /:id
```

---

## 📦 생성된 파일

### API 파일

```
backend/app/
├── api/
│   ├── __init__.py      # Blueprint 등록 (업데이트)
│   ├── posts.py         # Posts API
│   ├── categories.py    # Categories API
│   └── tags.py          # Tags API
├── utils/
│   ├── __init__.py
│   ├── errors.py        # 에러 핸들링
│   └── decorators.py    # 인증 데코레이터
└── __init__.py          # 에러 핸들러 & 로깅 등록 (업데이트)
```

### 테스트 파일

```
backend/tests/
└── test_api.py          # API 통합 테스트
```

### 문서

```
docs/implementation/
└── phase-03-implementation.md  # 이 문서
```

---

## 🔑 핵심 설계 결정

### 1. RESTful API 설계

**URL 구조**:
- 복수형 리소스 이름 (`/posts`, `/categories`)
- ID로 리소스 식별 (`/posts/:id`)
- Slug로도 조회 가능 (`/posts/slug/:slug`)

**HTTP 메서드**:
- GET - 조회
- POST - 생성 (또는 액션: `/posts/:id/publish`)
- PUT - 전체 수정
- DELETE - 삭제

### 2. 에러 처리 전략

**계층적 예외 구조**:
- `APIError` (기본)
  - `ValidationError` (400)
  - `AuthenticationError` (401)
  - `AuthorizationError` (403)
  - `NotFoundError` (404)
  - `ConflictError` (409)

**일관된 에러 응답**:
```json
{
  "error": true,
  "message": "설명",
  "status_code": 404
}
```

### 3. 인증/권한 분리

**3단계 권한 시스템**:
- **Public**: 인증 불필요
- **Editor**: 편집자 이상 (`@editor_required`)
- **Admin**: 관리자 전용 (`@admin_required`)

### 4. 페이지네이션

**SQLAlchemy paginate 사용**:
- `page`: 페이지 번호
- `per_page`: 페이지당 개수 (최대 100)
- 메타데이터 반환 (total, pages, has_next, has_prev)

---

## ✅ 검증

### API 테스트 (20+ 테스트 케이스)

**실행 방법** (Phase 4에서 진행 예정):
```bash
pytest tests/test_api.py -v
```

**테스트 커버리지**:
- Posts API: 목록, 상세, slug 조회, 404 에러
- Categories API: 목록, 상세, slug 조회, 404 에러
- Tags API: 목록, 상세, slug 조회, 정렬
- 에러 핸들링: 404, ping, health check

---

## 📊 통계

- **API 엔드포인트**: 22개
- **코드 라인**: 약 800줄
- **테스트 케이스**: 20+개
- **에러 클래스**: 5개
- **데코레이터**: 3개

---

## 💡 배운 점

1. **Flask Blueprint**: 모듈화된 API 구조
2. **전역 에러 핸들러**: 일관된 에러 응답
3. **데코레이터 패턴**: 인증/권한 체크 재사용
4. **페이지네이션**: SQLAlchemy paginate 활용
5. **로깅**: 프로덕션 환경 로그 관리

---

## ⚠️ 주의사항

### JWT 미구현

Phase 3에서는 JWT 데코레이터만 정의했고, **실제 인증 API는 Phase 4에서 구현**합니다.

현재는 데코레이터가 있지만 JWT 토큰 없이는 보호된 엔드포인트에 접근할 수 없습니다.

### Migration 미실행

모델은 정의되었지만 **실제 데이터베이스 생성은 Phase 4에서 진행**합니다.

### 테스트 실행 불가

현재는 테스트 코드만 작성되었고, Python 패키지 설치 후 실행 가능합니다.

---

## 🔄 다음 단계 (Phase 4)

**Phase 4: JWT 인증 구현**

주요 작업:
1. Auth API 구현 (회원가입, 로그인, 토큰 갱신)
2. Password 검증 및 해싱
3. JWT 토큰 발급 및 검증
4. Refresh Token 관리
5. 인증 테스트

---

**Phase 3 완료 ✅**

다음: [Phase 4 - JWT 인증 구현](./phase-04-implementation.md)
