# NewsKoo Backend

Flask 기반 유머 콘텐츠 플랫폼 백엔드 API 서버

## 기술 스택

- **Framework**: Flask 3.0
- **Database**: SQLAlchemy (SQLite/PostgreSQL)
- **Authentication**: Flask-JWT-Extended
- **AI/LLM**: HuggingFace Transformers + EEVE-Korean-10.8B
- **Task Queue**: APScheduler
- **Testing**: pytest

## 디렉토리 구조

```
backend/
├── app/
│   ├── __init__.py           # Flask 앱 팩토리
│   ├── api/                  # API 라우트 (Blueprint)
│   │   ├── __init__.py
│   │   ├── auth.py          # 인증 API
│   │   ├── posts.py         # 게시물 API
│   │   └── admin.py         # 관리자 API
│   ├── models/              # SQLAlchemy 모델
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── post.py
│   │   └── source.py
│   ├── services/            # 비즈니스 로직
│   │   ├── __init__.py
│   │   ├── llm_service.py   # LLM 관리
│   │   ├── crawler.py       # Reddit 크롤러
│   │   └── scheduler.py     # 작업 스케줄러
│   ├── utils/               # 유틸리티 함수
│   │   ├── __init__.py
│   │   └── validators.py
│   └── config/              # 설정 파일
│       └── __init__.py
├── tests/                   # 테스트
├── scripts/                 # 유틸리티 스크립트
├── run.py                   # 앱 실행 파일
└── requirements.txt         # 의존성 패키지

## 설치 및 실행

### 1. 가상 환경 생성

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정

루트 디렉토리의 `.env.example`을 복사하여 `.env` 파일 생성

### 4. 데이터베이스 초기화

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 5. 개발 서버 실행

```bash
python run.py
```

서버가 `http://localhost:5000`에서 실행됩니다.

## API 엔드포인트

### Health Check
- `GET /health` - 서버 상태 확인
- `GET /api/ping` - API 연결 테스트

### 인증 (추후 Phase 4에서 구현)
- `POST /api/auth/register` - 회원가입
- `POST /api/auth/login` - 로그인
- `POST /api/auth/refresh` - 토큰 갱신

### 게시물 (추후 Phase에서 구현)
- `GET /api/posts` - 게시물 목록
- `GET /api/posts/:id` - 게시물 상세
- `POST /api/posts` - 게시물 생성 (관리자)
- `PUT /api/posts/:id` - 게시물 수정 (관리자)
- `DELETE /api/posts/:id` - 게시물 삭제 (관리자)

## 테스트

```bash
pytest tests/ -v
pytest tests/ --cov=app
```

## 개발 가이드

### 새로운 API 엔드포인트 추가

1. `app/api/`에 새 파일 생성 (예: `categories.py`)
2. Blueprint 생성 및 라우트 정의
3. `app/api/__init__.py`에 import
4. 테스트 작성 (`tests/test_categories.py`)

### 새로운 모델 추가

1. `app/models/`에 새 파일 생성
2. SQLAlchemy 모델 정의
3. Migration 생성: `flask db migrate -m "Add new model"`
4. Migration 적용: `flask db upgrade`

## 참고 문서

- [Flask 공식 문서](https://flask.palletsprojects.com/)
- [SQLAlchemy 문서](https://docs.sqlalchemy.org/)
- [개발 로드맵](../DEVELOPMENT_ROADMAP.md)
