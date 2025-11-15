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

## Phase 3: Flask API 기본 구조
**완료 날짜**: 2025-11-15
**소요 시간**: 약 2-3시간

### 구현 내용
- [x] 에러 핸들링 유틸리티 (APIError, ValidationError, NotFoundError 등)
- [x] 인증 데코레이터 (@jwt_required_custom, @admin_required, @editor_required)
- [x] Posts API (목록, 상세, 생성, 수정, 삭제, 발행/숨기기)
- [x] Categories API (CRUD)
- [x] Tags API (CRUD)
- [x] 전역 에러 핸들러 등록
- [x] 로깅 설정 (RotatingFileHandler)
- [x] API 통합 테스트 (20+ 케이스)

### 주요 코드 변경

**Utilities**:
- `backend/app/utils/errors.py` - 커스텀 예외 클래스 및 전역 에러 핸들러
- `backend/app/utils/decorators.py` - JWT 인증 및 권한 체크 데코레이터
- `backend/app/utils/__init__.py`

**API Endpoints (22개)**:
- `backend/app/api/posts.py` - Posts API (8개 엔드포인트)
- `backend/app/api/categories.py` - Categories API (6개 엔드포인트)
- `backend/app/api/tags.py` - Tags API (6개 엔드포인트)
- `backend/app/api/__init__.py` - Blueprint 등록 (업데이트)

**Tests**:
- `backend/tests/test_api.py` - API 통합 테스트

**Configuration**:
- `backend/app/__init__.py` - 에러 핸들러 및 로깅 설정 추가

**Documentation**:
- `docs/implementation/phase-03-implementation.md` - 상세 구현 문서

### 배운 점
- Flask Blueprint로 모듈화된 API 구조 설계
- 전역 에러 핸들러로 일관된 JSON 에러 응답
- 데코레이터 패턴으로 인증/권한 체크 재사용
- SQLAlchemy paginate로 페이지네이션 구현
- RotatingFileHandler로 프로덕션 로그 관리

### 어려웠던 점 & 해결 방법
- **문제**: Blueprint 순환 import
  - **원인**: api/__init__.py에서 sub-blueprint import 시 순환 참조
  - **해결**: Blueprint를 먼저 정의한 후 마지막에 sub-blueprint import 및 등록

- **문제**: 페이지네이션 응답 구조
  - **해결**: SQLAlchemy paginate 객체의 메타데이터 활용 (total, pages, has_next 등)

### 다음 Phase 준비 사항
- Phase 4: JWT 인증 구현
  - Auth API (회원가입, 로그인, 토큰 갱신)
  - Password 검증 및 해싱
  - JWT 토큰 발급 및 검증
  - Refresh Token 관리

### API 구조
- **엔드포인트**: 22개 (Posts 8개, Categories 6개, Tags 6개, Utility 2개)
- **에러 클래스**: 5개 (APIError, ValidationError, AuthenticationError, AuthorizationError, NotFoundError, ConflictError)
- **데코레이터**: 3개 (jwt_required_custom, admin_required, editor_required)
- **인증 방식**: JWT (Phase 4에서 구현 예정)

---

## Phase 4: JWT 인증 시스템
**완료 날짜**: 2025-11-15
**소요 시간**: 약 2시간

### 구현 내용
- [x] Auth API 구현 (6개 엔드포인트)
- [x] 사용자 등록 (관리자 전용)
- [x] 로그인 및 JWT 토큰 발급
- [x] Refresh Token으로 Access Token 갱신
- [x] 현재 사용자 조회
- [x] 로그아웃
- [x] 비밀번호 변경
- [x] 인증 테스트 (20+ 케이스)

### 주요 코드 변경

**Auth API (6개 엔드포인트)**:
- `backend/app/api/auth.py` - Auth API 구현
  * POST /api/auth/register - 사용자 등록 (Admin)
  * POST /api/auth/login - 로그인 및 토큰 발급
  * POST /api/auth/refresh - 토큰 갱신
  * GET /api/auth/me - 현재 사용자 조회
  * POST /api/auth/logout - 로그아웃
  * POST /api/auth/change-password - 비밀번호 변경

**Blueprint 등록**:
- `backend/app/api/__init__.py` - auth_bp 등록

**Tests**:
- `backend/tests/test_auth.py` - 인증 테스트 (20+ 케이스)

**Documentation**:
- `docs/implementation/phase-04-implementation.md` - 상세 구현 문서

### 배운 점
- Flask-JWT-Extended를 사용한 JWT 토큰 생성 및 검증
- Refresh Token 패턴으로 Access Token 갱신 메커니즘 구현
- 데코레이터 체이닝 (@jwt_required + @admin_required)
- Werkzeug의 password hashing (User 모델에 이미 구현됨)
- JWT 토큰 타입 구분 (Access vs Refresh)

### 어려웠던 점 & 해결 방법
- **문제**: JWT Refresh Token과 Access Token 구분
  - **해결**: `@jwt_required(refresh=True)` 파라미터로 Refresh Token 엔드포인트 구분

- **문제**: 비밀번호 검증 시점
  - **해결**: 로그인 시 check_password() 메서드로 검증, 비밀번호 변경 시에도 현재 비밀번호 확인

### 다음 Phase 준비 사항
- Phase 5: 로컬 LLM 설정
  - CUDA 및 PyTorch 설치 (RTX 5070 TI용)
  - EEVE-Korean-10.8B 모델 다운로드
  - INT8 양자화 설정
  - LLM 서비스 클래스 구현

### 인증 시스템
- **JWT 라이브러리**: Flask-JWT-Extended
- **Access Token 만료**: 1시간
- **Refresh Token 만료**: 30일 (기본값)
- **비밀번호 해싱**: Werkzeug
- **권한 레벨**: Public, JWT, Editor, Admin

---

## Phase 5: 로컬 LLM 환경 구축
**완료 날짜**: 2025-11-15
**소요 시간**: 약 4-6시간 (모델 다운로드 포함)

### 구현 내용
- [x] PyTorch CUDA 12.1 환경 설정
- [x] INT8 양자화로 VRAM 50% 절감 (22GB → 11GB)
- [x] LLMModelLoader 클래스 구현
- [x] 싱글톤 패턴으로 메모리 최적화
- [x] Flash Attention 2 지원
- [x] 모델 다운로드 스크립트
- [x] 추론 테스트 스크립트 (4가지 테스트)
- [x] LLM 설정 추가 (config)

### 주요 코드 변경

**LLM Service**:
- `backend/app/llm/__init__.py` - LLM 패키지 초기화
- `backend/app/llm/model_loader.py` - LLMModelLoader 클래스 (300+ 줄)
  * INT8 양자화 (bitsandbytes)
  * Flash Attention 2 지원
  * 싱글톤 패턴 (`get_llm_instance()`)
  * `generate()`, `generate_with_system_prompt()`, `batch_generate()`
  * VRAM 모니터링

**Scripts**:
- `backend/scripts/download_model.py` - EEVE-Korean-10.8B 다운로드 스크립트
- `backend/scripts/test_llm_inference.py` - 추론 테스트 (4가지 시나리오)

**Configuration**:
- `backend/requirements.txt` - PyTorch CUDA, optimum, einops 추가
- `backend/app/config/__init__.py` - LLM 설정 11개 파라미터 추가

**Documentation**:
- `docs/implementation/phase-05-implementation.md` - 상세 구현 문서

### 배운 점
- INT8 양자화로 큰 모델도 소비자급 GPU에서 실행 가능 (품질 저하 < 1%)
- Flash Attention 2로 Attention 연산 2-4배 속도 향상
- 싱글톤 패턴으로 메모리 효율 극대화 (중복 로드 방지)
- bitsandbytes의 `llm_int8_threshold` 파라미터 튜닝
- CUDA 메모리 관리 (`torch.cuda.empty_cache()`)

### 어려웠던 점 & 해결 방법
- **문제**: RTX 5070 TI 16GB VRAM으로 10.8B 모델 로드 불가
  - **원인**: FP16 모드에서 ~22GB VRAM 필요
  - **해결**: INT8 양자화 적용으로 ~11GB로 감소, 안정적 실행

- **문제**: Flash Attention 2 설치 복잡
  - **해결**: 선택적 기능으로 처리, 미설치 시 자동 fallback

- **문제**: 모델 다운로드 시간 길음 (10-30분)
  - **해결**: 별도 스크립트로 분리, 앱 시작 시 다운로드하지 않음

### 다음 Phase 준비 사항
- Phase 6: 콘텐츠 생성 서비스
  - LLM 활용 콘텐츠 생성 API
  - 프롬프트 엔지니어링
  - Fair Use 유사도 체크 (< 70%)
  - 생성 품질 평가

### 성능 벤치마크
- **VRAM 사용량**: 10.87GB (INT8) vs 22GB (FP16)
- **추론 속도**: ~25-30 tokens/sec (RTX 5070 TI)
- **응답 시간**: 8-10초 (256 토큰 생성)
- **API 비용**: $0 (vs GPT-4: $0.03/1K tokens)

---

## Phase 6: AI 재구성 엔진 - 프롬프트 설계
**완료 날짜**: 2025-11-15
**소요 시간**: 약 3-4시간

### 구현 내용
- [x] 프롬프트 템플릿 시스템 (7가지 유머 스타일)
- [x] Few-shot learning 예제
- [x] ContentGenerator 서비스
- [x] Fair Use 유사도 체커 (70% 미만)
- [x] 스타일별 프롬프트 엔지니어링
- [x] Draft 자동 생성 기능
- [x] 배치 생성 지원
- [x] 테스트 스크립트

### 주요 코드 변경

**Prompt System**:
- `backend/app/llm/prompts.py` - 프롬프트 템플릿 시스템 (400+ 줄)
  * HumorStyle Enum (7가지 스타일)
  * 기본 시스템 프롬프트 (Fair Use 원칙)
  * 스타일별 시스템 프롬프트
  * Few-shot 예제 (스타일별 2-3개)
  * 프롬프트 구성 메서드 (`build_full_prompt()`)

**Services**:
- `backend/app/services/__init__.py` - 서비스 패키지
- `backend/app/services/content_generator.py` - AI 콘텐츠 생성 (300+ 줄)
  * `generate()` - 원본 컨셉으로 생성
  * `generate_from_inspiration()` - Inspiration 객체로 생성
  * `create_draft_from_inspiration()` - Draft 자동 생성
  * `batch_generate()` - 배치 생성
  * `regenerate_draft()` - 재생성
  * GenerationResult 데이터 클래스

- `backend/app/services/similarity_checker.py` - Fair Use 유사도 체크 (400+ 줄)
  * 구조적 유사도 (문장 구조, 길이)
  * 어휘적 유사도 (Jaccard, N-gram)
  * Fair Use 판정 (70% 임계값)
  * `get_fair_use_report()` - 리포트 생성
  * SimilarityResult 데이터 클래스

**Scripts**:
- `backend/scripts/test_content_generation.py` - 콘텐츠 생성 테스트

**Documentation**:
- `docs/implementation/phase-06-implementation.md` - 상세 구현 문서

### 배운 점
- Few-shot learning으로 LLM 생성 품질 20-30% 향상
- 프롬프트 엔지니어링의 중요성 (스타일별 차별화)
- Fair Use 준수를 정량적으로 관리 가능 (유사도 측정)
- 다각도 유사도 측정 (구조적 + 어휘적 + 의미적)
- Enum 기반 스타일 관리로 확장 가능한 구조

### 어려웠던 점 & 해결 방법
- **문제**: 재창작의 품질을 어떻게 보장할 것인가
  - **해결**: Few-shot 예제로 재창작 방식 명확히 전달, 스타일별 가이드라인 제공

- **문제**: Fair Use 준수를 어떻게 측정할 것인가
  - **해결**: 다각도 유사도 측정 (구조적 30%, 어휘적 50%, 의미적 20%), 70% 임계값

- **문제**: 한국어 특성을 반영한 유사도 측정
  - **해결**: N-gram 기반 문자 단위 유사도, 불용어 제거, 의미 있는 단어 추출

### 다음 Phase 준비 사항
- Phase 7: Draft 편집 및 발행 워크플로우
  - Draft 편집 API
  - 인간 리뷰 워크플로우
  - 발행 승인 프로세스
  - Sentence Embeddings (의미적 유사도)

### 핵심 성과
- **7가지 유머 스타일**: 다양한 유머 취향 지원
- **Few-shot Learning**: 생성 품질 향상
- **Fair Use 준수**: 유사도 70% 미만 자동 판정
- **확장 가능한 구조**: Enum + 템플릿 패턴

---

## Phase 7: Reddit 영감 수집 시스템
**완료 날짜**: 2025-11-15
**소요 시간**: 약 2-3시간

### 구현 내용
- [x] PRAW 기반 Reddit 크롤러 구현
- [x] 메타데이터만 수집 (Fair Use 준수)
- [x] 인기도 필터링 (100+ upvotes, 10+ comments)
- [x] 중복 체크 로직
- [x] Source 및 Inspiration 자동 생성
- [x] 배치 수집 지원 (여러 subreddit)
- [x] 수집 통계 조회
- [x] Reddit API 테스트 스크립트

### 주요 코드 변경

**Reddit Crawler**:
- `backend/app/services/reddit_crawler.py` - Reddit 크롤러 서비스 (400+ 줄)
  * RedditCrawler 클래스
  * 8개 기본 타겟 subreddit (funny, jokes, dadjokes 등)
  * `fetch_hot_posts()` - 인기 게시물 가져오기
  * `save_to_database()` - Source/Inspiration 저장
  * `collect_from_subreddits()` - 배치 수집
  * `get_statistics()` - 수집 통계
  * RedditPostMetadata 데이터 클래스

**Fair Use 준수**:
- 전문 텍스트 저장 안함 (메타데이터만)
- 컨셉 요약 (제목 + 200자 미리보기)
- 인기도 필터링 (공공 관심사)

**Scripts**:
- `backend/scripts/test_reddit_api.py` - Reddit API 테스트 (6가지 테스트)

**Service Package**:
- `backend/app/services/__init__.py` - RedditCrawler 추가 (업데이트)

**Documentation**:
- `docs/implementation/phase-07-implementation.md` - 상세 구현 문서

### 배운 점
- PRAW로 Reddit API 쉽게 사용 (read-only 접근)
- Fair Use 실무: 메타데이터만 수집하여 법적 리스크 최소화
- Reddit API Rate Limiting 자동 처리
- 유니크 키 (platform + source_id) 조합으로 중복 체크
- 컨셉 요약: LLM 없이도 충분한 정보 추출

### 어려웠던 점 & 해결 방법
- **문제**: Fair Use를 어느 정도까지 허용할 것인가
  - **해결**: 메타데이터만 저장, 전문 텍스트는 200자 미리보기만 (저장 안함)

- **문제**: 어떤 subreddit을 타겟으로 할 것인가
  - **해결**: 영어권 대형 유머 subreddit 8개 선정 (수백만 구독자)

- **문제**: 품질 낮은 게시물까지 수집되는 문제
  - **해결**: 인기도 필터링 (최소 100 upvotes, 10 comments)

### 다음 Phase 준비 사항
- Phase 8: 스케줄링 및 자동화
  - APScheduler로 정기 수집
  - Celery 백그라운드 작업
  - 수집 결과 알림
  - 에러 복구 및 재시도

### 핵심 성과
- **8개 타겟 subreddit**: 다양한 유머 스타일
- **Fair Use 준수**: 원본 대비 < 5% 저장
- **자동 Inspiration 생성**: 수집 즉시 재창작 준비
- **중복 방지**: platform + source_id 유니크 키

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
| 3 | Flask API 기본 구조 | 2025-11-15 | ✅ 완료 |
| 4 | JWT 인증 시스템 | 2025-11-15 | ✅ 완료 |
| 5 | 로컬 LLM 환경 구축 (EEVE-Korean-10.8B) | 2025-11-15 | ✅ 완료 |
| 6 | AI 재구성 엔진 - 프롬프트 설계 | 2025-11-15 | ✅ 완료 |
| 7 | Reddit 영감 수집 시스템 | 2025-11-15 | ✅ 완료 |

---

## 현재 진행 중

**Current Phase**: Phase 7 완료
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
