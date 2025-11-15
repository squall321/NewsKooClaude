# 개발 진행 상황 추적

## 사용법
각 Phase를 완료할 때마다 아래 템플릿을 사용하여 기록합니다.

---

## Phase 1: 프로젝트 구조 및 개발 환경 설정
**완료 날짜**: 2025-11-15
**소요 시간**: 약 2시간

### 구현 내용
- [x] Vite React TypeScript 프론트엔드 프로젝트 생성
- [x] 필수 패키지 설치 (React Router, React Query, Axios, Tailwind CSS)
- [x] Flask 백엔드 프로젝트 구조 생성
- [x] ESLint 및 Prettier 설정
- [x] 환경변수 관리 (.env.example)
- [x] 프론트엔드/백엔드 디렉토리 구조 설계
- [x] README.md 문서 작성 (frontend, backend)
- [x] .gitignore 설정

### 주요 코드 변경

**Frontend**:
- `frontend/` - Vite React TypeScript 프로젝트 생성
- `frontend/tailwind.config.js` - Tailwind CSS 설정
- `frontend/postcss.config.js` - PostCSS 설정
- `frontend/eslint.config.js` - ESLint + Prettier 통합
- `frontend/src/index.css` - Tailwind directives 추가
- `frontend/src/components/` - 컴포넌트 디렉토리 구조
- `frontend/.env.example` - 환경변수 템플릿

**Backend**:
- `backend/app/__init__.py` - Flask 앱 팩토리 함수
- `backend/app/config/__init__.py` - 환경별 설정 (Dev, Prod, Test)
- `backend/app/api/__init__.py` - API Blueprint
- `backend/run.py` - Flask 실행 스크립트
- `backend/requirements.txt` - Python 의존성 패키지
- `backend/README.md` - 백엔드 문서
- `.env.example` - 환경변수 템플릿 (루트)

**기타**:
- `.gitignore` - Git 제외 파일 설정
- `PROGRESS.md` - 이 문서 업데이트

### 배운 점
- Vite의 빠른 빌드 속도와 HMR (Hot Module Replacement) 장점 체감
- Tailwind CSS의 유틸리티 클래스 기반 스타일링 방식 이해
- Flask 앱 팩토리 패턴으로 확장 가능한 구조 설계 가능
- Pydantic Settings를 사용한 타입 안전한 환경변수 관리

### 어려웠던 점 & 해결 방법
- **문제**: `npx tailwindcss init` 명령어가 실패
  - **원인**: npm 실행 컨텍스트 문제
  - **해결**: 수동으로 tailwind.config.js와 postcss.config.js 파일 생성

- **문제**: ESLint flat config 구조 이해
  - **해결**: Vite가 생성한 최신 ESLint 설정을 기반으로 Prettier 플러그인 추가

### 다음 Phase 준비 사항
- Phase 2: 데이터베이스 설계 및 모델 구현
  - SQLAlchemy 모델 정의 (User, Post, Source 등)
  - ERD 다이어그램 작성
  - Migration 설정

### 기술 스택 확정
- **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS
- **Backend**: Flask 3.0 + SQLAlchemy + Pydantic
- **Database**: SQLite (dev) → PostgreSQL (prod)
- **AI/LLM**: EEVE-Korean-10.8B (로컬 RTX 5070 TI)

---

## Phase 2: 데이터베이스 설계 및 모델 정의
**완료 날짜**: 2025-11-15
**소요 시간**: 약 3-4시간

### 구현 내용
- [x] ERD (Entity Relationship Diagram) 설계
- [x] BaseModel 및 TimestampMixin 생성
- [x] User 모델 (비밀번호 해싱, 권한 관리)
- [x] Category 모델 (slug 자동 생성)
- [x] Tag 모델 (N:N 중간 테이블)
- [x] Source 모델 (외부 소스 메타데이터)
- [x] Inspiration 모델 (Fair Use 유사도 관리)
- [x] WritingStyle 모델 (AI 프롬프트 템플릿)
- [x] Draft 모델 (초안, 상태 관리)
- [x] Post 모델 (발행된 게시물, slug 중복 방지)
- [x] Seed 데이터 생성 스크립트
- [x] 모델 테스트 작성 (20+ 테스트 케이스)

### 주요 코드 변경

**Models (8개 핵심 모델)**:
- `backend/app/models/base.py` - BaseModel, TimestampMixin
- `backend/app/models/user.py` - User (인증, 권한)
- `backend/app/models/category.py` - Category
- `backend/app/models/tag.py` - Tag, post_tags 중간 테이블
- `backend/app/models/source.py` - Source (메타데이터만 저장)
- `backend/app/models/inspiration.py` - Inspiration (재창작 아이디어)
- `backend/app/models/writing_style.py` - WritingStyle (AI 프롬프트)
- `backend/app/models/draft.py` - Draft (작성 중인 콘텐츠)
- `backend/app/models/post.py` - Post (발행된 게시물)
- `backend/app/models/__init__.py` - 모든 모델 export

**Scripts & Tests**:
- `backend/scripts/seed_data.py` - 개발용 초기 데이터 생성
- `backend/tests/conftest.py` - pytest fixtures
- `backend/tests/test_models.py` - 모델 단위 테스트

**Documentation**:
- `docs/DATABASE_ERD.md` - ERD 다이어그램 및 스키마 설계
- `docs/implementation/phase-02-implementation.md` - 상세 구현 문서

**Configuration**:
- `backend/requirements.txt` - python-slugify, Werkzeug 추가
- `backend/app/__init__.py` - models import 추가

### 배운 점
- SQLAlchemy relationship 설정 (`back_populates` vs `backref`)
- Mixin 패턴으로 공통 기능 재사용
- Slug 중복 방지 로직 (자동으로 -1, -2 추가)
- Fair Use 준수를 위한 유사도 점수 관리
- 상태 관리 (Enum 대신 문자열 + 메서드)
- pytest fixtures로 테스트 데이터 관리

### 어려웠던 점 & 해결 방법
- **문제**: 모델 간 순환 참조 (circular import)
  - **원인**: models/__init__.py에서 모든 모델 import 시 순환 참조 발생
  - **해결**: 지연 import 사용 또는 관계 설정 시 문자열로 모델명 지정

- **문제**: Post-Tag N:N 관계 설정
  - **해결**: `db.Table`로 중간 테이블 정의 후 `secondary` 파라미터 사용

- **문제**: Slug 중복 방지
  - **해결**: `_generate_unique_slug()` 클래스 메서드로 중복 체크 및 카운터 추가

### 다음 Phase 준비 사항
- Phase 3: Flask API 기본 구조
  - Flask-Migrate 초기화 및 Migration 생성
  - REST API 엔드포인트 구현 (CRUD)
  - Request/Response 검증
  - 에러 핸들링
  - API 문서화

### 데이터베이스 설계
- **모델 수**: 8개 (User, Post, Draft, Category, Tag, Source, Inspiration, WritingStyle)
- **관계**:
  - 1:N - User→Post, User→Draft, Category→Post, Source→Inspiration, WritingStyle→Draft
  - 1:1 - Inspiration↔Draft, Draft↔Post
  - N:N - Post↔Tag (중간 테이블: post_tags)
- **Fair Use 준수**: Source는 메타데이터만 저장, Inspiration에서 유사도 관리
- **워크플로우**: Source → Inspiration → Draft → Post

---

## Phase [번호]: [제목]
**완료 날짜**: YYYY-MM-DD
**소요 시간**: X시간/일

### 구현 내용
- [ ] 체크리스트 항목 1
- [ ] 체크리스트 항목 2

### 주요 코드 변경
```
파일 경로: 변경 내용 요약
```

### 배운 점
-

### 어려웠던 점 & 해결 방법
-

### 다음 Phase 준비 사항
-

### 스크린샷 (선택)
<!-- 필요시 스크린샷 추가 -->

---

## 완료된 Phase 목록

| Phase | 제목 | 완료일 | 상태 |
|-------|------|--------|------|
| 1 | 프로젝트 구조 및 개발 환경 설정 | 2025-11-15 | ✅ 완료 |
| 2 | 데이터베이스 설계 및 모델 정의 | 2025-11-15 | ✅ 완료 |

---

## 현재 진행 중

**Current Phase**: Phase 2 완료
**목표 완료일**: 2025-11-15
**진행률**: 100%

---

## 메모 및 아이디어

### 기술 결정
-

### 개선 아이디어
-

### 참고 링크
-
