# Phase 1: 프로젝트 구조 및 개발 환경 설정

**난이도**: ⭐⭐☆☆☆
**예상 소요 시간**: 2-3시간
**우선순위**: P0 (필수)

## 목표

프론트엔드(React + TypeScript + Vite)와 백엔드(Flask) 프로젝트의 기본 골격을 생성하고, 개발에 필요한 도구들을 설정합니다.

## 선행 요구사항

### 필수 소프트웨어
- Node.js 18+ 설치 확인
- Python 3.10+ 설치 확인
- Git 설치 확인
- 코드 에디터 (VSCode 권장)

### 확인 명령어
```bash
node --version   # v18.0.0 이상
npm --version    # v9.0.0 이상
python --version # 3.10.0 이상
git --version    # 2.0.0 이상
```

---

## 구현 단계

### 1단계: 프로젝트 루트 디렉토리 확인

```bash
# 현재 위치 확인
pwd
# /home/user/NewsKooClaude

# 디렉토리 구조 확인
ls -la
```

**예상 출력**:
```
.git/
docs/
DEVELOPMENT_ROADMAP.md
PROGRESS.md
README.md
```

---

### 2단계: Frontend 프로젝트 생성 (Vite + React + TypeScript)

#### 2-1. Vite 프로젝트 생성

```bash
# npm을 사용한 Vite 프로젝트 생성
npm create vite@latest frontend -- --template react-ts

# 또는 대화형 생성
npm create vite@latest
# Project name: frontend
# Framework: React
# Variant: TypeScript
```

#### 2-2. Frontend 디렉토리 이동 및 의존성 설치

```bash
cd frontend
npm install
```

#### 2-3. 추가 의존성 설치

```bash
# 라우팅
npm install react-router-dom

# 상태 관리 및 API
npm install @tanstack/react-query axios

# 스타일링
npm install styled-components
npm install @types/styled-components -D

# UI 라이브러리 (선택사항)
npm install @radix-ui/react-dialog @radix-ui/react-dropdown-menu

# 유틸리티
npm install clsx date-fns

# 마크다운 에디터 (나중에 사용)
npm install @uiw/react-md-editor

# 아이콘
npm install lucide-react
```

#### 2-4. 개발 도구 설치

```bash
# ESLint & Prettier
npm install -D eslint prettier eslint-config-prettier eslint-plugin-react-hooks
npm install -D @typescript-eslint/eslint-plugin @typescript-eslint/parser
```

#### 2-5. ESLint 설정 파일 생성

**frontend/.eslintrc.json**:
```json
{
  "env": {
    "browser": true,
    "es2021": true
  },
  "extends": [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:react-hooks/recommended",
    "prettier"
  ],
  "parser": "@typescript-eslint/parser",
  "parserOptions": {
    "ecmaVersion": "latest",
    "sourceType": "module",
    "ecmaFeatures": {
      "jsx": true
    }
  },
  "plugins": ["@typescript-eslint", "react-refresh"],
  "rules": {
    "react-refresh/only-export-components": "warn",
    "@typescript-eslint/no-unused-vars": ["warn", { "argsIgnorePattern": "^_" }]
  }
}
```

#### 2-6. Prettier 설정 파일 생성

**frontend/.prettierrc**:
```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 80,
  "tabWidth": 2,
  "useTabs": false,
  "arrowParens": "always",
  "endOfLine": "lf"
}
```

#### 2-7. 환경 변수 파일 생성

**frontend/.env.example**:
```env
# API URL
VITE_API_URL=http://localhost:5000/api/v1

# 개발 모드
VITE_DEV_MODE=true
```

**frontend/.env**:
```env
VITE_API_URL=http://localhost:5000/api/v1
VITE_DEV_MODE=true
```

#### 2-8. 디렉토리 구조 생성

```bash
# frontend 디렉토리 안에서 실행
mkdir -p src/{components,pages,hooks,api,styles,utils,types,contexts}
mkdir -p src/components/{common,post,admin,layout}
mkdir -p src/pages/admin
mkdir -p public/assets
```

**생성된 구조**:
```
frontend/
├── src/
│   ├── components/
│   │   ├── common/      # Button, Card, Modal 등
│   │   ├── post/        # 게시물 관련 컴포넌트
│   │   ├── admin/       # 관리자 전용 컴포넌트
│   │   └── layout/      # Header, Footer, Sidebar
│   ├── pages/           # 페이지 컴포넌트
│   │   └── admin/       # 관리자 페이지
│   ├── hooks/           # 커스텀 훅
│   ├── api/             # API 클라이언트
│   ├── styles/          # 글로벌 스타일, 테마
│   ├── utils/           # 유틸리티 함수
│   ├── types/           # TypeScript 타입 정의
│   └── contexts/        # React Context
├── public/
│   └── assets/          # 정적 파일
├── .env
├── .env.example
├── .eslintrc.json
├── .prettierrc
├── package.json
└── vite.config.ts
```

#### 2-9. 기본 타입 정의 생성

**frontend/src/types/index.ts**:
```typescript
// 게시물 타입
export interface Post {
  id: string;
  title: string;
  content: string;
  excerpt?: string;
  thumbnail?: string;
  category: Category;
  tags: Tag[];
  author: User;
  viewCount: number;
  createdAt: string;
  updatedAt: string;
  published: boolean;
  originalSource?: string; // Reddit URL
}

// 카테고리 타입
export interface Category {
  id: string;
  name: string;
  slug: string;
  icon?: string;
  color?: string;
}

// 태그 타입
export interface Tag {
  id: string;
  name: string;
}

// 사용자 타입
export interface User {
  id: string;
  username: string;
  email: string;
  role: 'admin' | 'writer';
}

// 초안 타입
export interface Draft {
  id: string;
  title: string;
  content: string;
  status: 'writing' | 'ai_pending' | 'review';
  inspirationId?: string;
  createdAt: string;
  updatedAt: string;
}

// 영감 소스 타입
export interface Inspiration {
  id: string;
  title: string;
  url: string;
  source: 'reddit' | 'twitter' | 'other';
  subreddit?: string;
  upvotes?: number;
  createdAt: string;
  bookmarked: boolean;
  hidden: boolean;
}
```

---

### 3단계: Backend 프로젝트 생성 (Flask)

#### 3-1. Backend 디렉토리 생성

```bash
# 프로젝트 루트로 이동
cd ..
mkdir backend
cd backend
```

#### 3-2. Python 가상환경 생성

```bash
# venv 생성
python -m venv venv

# 활성화
# Linux/Mac:
source venv/bin/activate

# Windows:
# venv\Scripts\activate

# 프롬프트에 (venv)가 표시되는지 확인
```

#### 3-3. 필수 패키지 설치

```bash
# Flask 핵심
pip install Flask==3.0.0
pip install flask-cors==4.0.0
pip install flask-sqlalchemy==3.1.1
pip install flask-migrate==4.0.5
pip install flask-jwt-extended==4.5.3

# 데이터베이스
pip install psycopg2-binary==2.9.9  # PostgreSQL
pip install redis==5.0.1

# 환경 변수
pip install python-dotenv==1.0.0

# 크롤링
pip install praw==7.7.1  # Reddit API
pip install beautifulsoup4==4.12.2
pip install requests==2.31.0

# 스케줄링
pip install APScheduler==3.10.4

# 이미지 처리
pip install Pillow==10.1.0

# 개발 도구
pip install black==23.11.0
pip install flake8==6.1.0
pip install pytest==7.4.3
pip install pytest-flask==1.3.0

# requirements.txt 생성
pip freeze > requirements.txt
```

#### 3-4. Backend 디렉토리 구조 생성

```bash
mkdir -p app/{api,models,services,llm,utils}
mkdir -p app/api/v1
mkdir -p migrations
mkdir -p static/uploads/images
mkdir -p tests
mkdir -p logs
mkdir -p scripts
```

**생성된 구조**:
```
backend/
├── app/
│   ├── __init__.py
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── posts.py
│   │       ├── drafts.py
│   │       ├── inspirations.py
│   │       ├── ai_assistant.py
│   │       └── auth.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── post.py
│   │   ├── draft.py
│   │   ├── inspiration.py
│   │   ├── user.py
│   │   └── category.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_rewriter.py
│   │   ├── crawler.py
│   │   └── image_processor.py
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── model_loader.py
│   │   ├── prompts.py
│   │   └── inference.py
│   └── utils/
│       ├── __init__.py
│       └── helpers.py
├── migrations/
├── static/
│   └── uploads/
│       └── images/
├── tests/
├── logs/
├── scripts/
├── venv/
├── .env
├── .env.example
├── requirements.txt
├── config.py
└── run.py
```

#### 3-5. 환경 변수 파일 생성

**backend/.env.example**:
```env
# Flask
FLASK_APP=app
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-in-production

# 데이터베이스
DATABASE_URL=sqlite:///humorhub.db
# DATABASE_URL=postgresql://user:password@localhost:5432/humorhub

# Redis (선택적)
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ACCESS_TOKEN_EXPIRES=3600

# Reddit API
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=HumorHub/1.0

# 로컬 LLM 설정
LLM_MODEL_NAME=EEVE-Korean-10.8B-v1.0
LLM_MODEL_PATH=./models/EEVE-Korean-10.8B-INT8
LLM_DEVICE=cuda
LLM_QUANTIZATION=int8
LLM_MAX_LENGTH=1024

# 업로드 설정
UPLOAD_FOLDER=./static/uploads
MAX_UPLOAD_SIZE=10485760  # 10MB
```

**backend/.env**:
```env
# .env.example 내용 복사 후 실제 값 입력
FLASK_APP=app
FLASK_ENV=development
SECRET_KEY=dev-secret-key-change-later
DATABASE_URL=sqlite:///humorhub.db
```

#### 3-6. Flask 설정 파일 생성

**backend/config.py**:
```python
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    """기본 설정"""
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'

    # 데이터베이스
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///humorhub.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Redis
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'

    # JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        seconds=int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 3600))
    )

    # 업로드
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or './static/uploads'
    MAX_UPLOAD_SIZE = int(os.environ.get('MAX_UPLOAD_SIZE', 10485760))
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    # LLM
    LLM_MODEL_NAME = os.environ.get('LLM_MODEL_NAME')
    LLM_MODEL_PATH = os.environ.get('LLM_MODEL_PATH')
    LLM_DEVICE = os.environ.get('LLM_DEVICE', 'cuda')
    LLM_QUANTIZATION = os.environ.get('LLM_QUANTIZATION', 'int8')
    LLM_MAX_LENGTH = int(os.environ.get('LLM_MAX_LENGTH', 1024))

    # Reddit
    REDDIT_CLIENT_ID = os.environ.get('REDDIT_CLIENT_ID')
    REDDIT_CLIENT_SECRET = os.environ.get('REDDIT_CLIENT_SECRET')
    REDDIT_USER_AGENT = os.environ.get('REDDIT_USER_AGENT', 'HumorHub/1.0')


class DevelopmentConfig(Config):
    """개발 환경 설정"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """프로덕션 환경 설정"""
    DEBUG = False
    TESTING = False

    # 프로덕션에서는 SQLite 대신 PostgreSQL 사용
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


class TestingConfig(Config):
    """테스트 환경 설정"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
```

#### 3-7. Flask 애플리케이션 초기화

**backend/app/__init__.py**:
```python
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from config import config
import os

# Extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app(config_name=None):
    """Flask 애플리케이션 팩토리"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # CORS 설정
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5173"],  # Vite 개발 서버
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # Extensions 초기화
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # 업로드 폴더 생성
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Blueprints 등록 (나중에 추가)
    # from app.api.v1 import posts, drafts, auth
    # app.register_blueprint(posts.bp)
    # app.register_blueprint(drafts.bp)
    # app.register_blueprint(auth.bp)

    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'ok', 'message': 'HumorHub API is running'}

    return app
```

#### 3-8. 애플리케이션 실행 파일 생성

**backend/run.py**:
```python
from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
```

#### 3-9. 개발 도구 설정

**backend/.flake8**:
```ini
[flake8]
max-line-length = 100
exclude = venv,migrations,__pycache__
ignore = E203, W503
```

**backend/pyproject.toml** (Black 설정):
```toml
[tool.black]
line-length = 100
target-version = ['py310']
include = '\.pyi?$'
exclude = '''
/(
    \.git
  | \.venv
  | venv
  | migrations
  | __pycache__
)/
'''
```

---

### 4단계: Git 설정

#### 4-1. .gitignore 업데이트

**프로젝트 루트의 .gitignore**:
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
*.egg-info/

# Node
node_modules/
dist/
build/
.parcel-cache/

# Environment
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*.sublime-*

# OS
.DS_Store
Thumbs.db
*.log

# Database
*.db
*.sqlite
*.sqlite3

# Uploads
backend/static/uploads/*
!backend/static/uploads/.gitkeep

# Models (대용량)
backend/models/
*.bin
*.safetensors

# Logs
logs/
*.log

# Test
.pytest_cache/
.coverage
htmlcov/

# Docker
docker-compose.override.yml
```

#### 4-2. 빈 디렉토리 유지용 파일 생성

```bash
# 업로드 폴더 보존
touch backend/static/uploads/.gitkeep
touch backend/logs/.gitkeep
```

---

### 5단계: 개발 서버 실행 테스트

#### 5-1. Backend 서버 실행

```bash
# backend 디렉토리에서
cd backend
source venv/bin/activate
python run.py
```

**예상 출력**:
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://0.0.0.0:5000
```

**테스트**:
```bash
# 다른 터미널에서
curl http://localhost:5000/health
```

**예상 응답**:
```json
{"status":"ok","message":"HumorHub API is running"}
```

#### 5-2. Frontend 서버 실행

```bash
# 새 터미널에서
cd frontend
npm run dev
```

**예상 출력**:
```
VITE v5.0.0  ready in 500 ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

**브라우저에서 확인**: http://localhost:5173

---

## 완료 체크리스트

### Frontend
- [ ] Vite + React + TypeScript 프로젝트 생성
- [ ] 필수 의존성 설치 (react-router-dom, react-query, axios 등)
- [ ] ESLint, Prettier 설정
- [ ] 환경 변수 파일 (.env.example, .env) 생성
- [ ] 디렉토리 구조 생성 (components, pages, hooks 등)
- [ ] 기본 타입 정의 (src/types/index.ts)
- [ ] 개발 서버 실행 확인 (http://localhost:5173)

### Backend
- [ ] Python 가상환경 생성 및 활성화
- [ ] Flask 및 필수 패키지 설치
- [ ] requirements.txt 생성
- [ ] 디렉토리 구조 생성 (app, models, services 등)
- [ ] 환경 변수 파일 (.env.example, .env) 생성
- [ ] config.py 작성
- [ ] Flask 앱 초기화 (app/__init__.py)
- [ ] run.py 작성
- [ ] Health check 엔드포인트 테스트 성공
- [ ] 개발 서버 실행 확인 (http://localhost:5000)

### Git & 문서
- [ ] .gitignore 업데이트
- [ ] .gitkeep 파일 생성
- [ ] PROGRESS.md에 Phase 1 완료 기록

---

## 예상 디렉토리 구조 (최종)

```
NewsKooClaude/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── api/
│   │   ├── styles/
│   │   ├── utils/
│   │   ├── types/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── public/
│   ├── .env
│   ├── .env.example
│   ├── .eslintrc.json
│   ├── .prettierrc
│   ├── package.json
│   └── vite.config.ts
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── api/
│   │   ├── models/
│   │   ├── services/
│   │   ├── llm/
│   │   └── utils/
│   ├── migrations/
│   ├── static/uploads/
│   ├── tests/
│   ├── logs/
│   ├── scripts/
│   ├── venv/
│   ├── .env
│   ├── .env.example
│   ├── .flake8
│   ├── pyproject.toml
│   ├── config.py
│   ├── requirements.txt
│   └── run.py
│
├── docs/
│   ├── phases/
│   ├── DEVELOPMENT_ROADMAP.md
│   ├── LOCAL_LLM_SETUP.md
│   └── PROGRESS.md
│
├── .gitignore
└── README.md
```

---

## 문제 해결

### 문제 1: npm install 실패
**증상**: `EACCES` 권한 오류

**해결**:
```bash
sudo chown -R $USER:$USER ~/.npm
sudo chown -R $USER:$USER frontend/node_modules
```

### 문제 2: Python 가상환경 활성화 안됨
**증상**: `(venv)` 표시가 안 나옴

**해결**:
```bash
# Linux/Mac
source venv/bin/activate

# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Windows CMD
venv\Scripts\activate.bat
```

### 문제 3: Flask 서버 실행 시 포트 충돌
**증상**: `Address already in use`

**해결**:
```bash
# 5000번 포트 사용 프로세스 종료
lsof -ti:5000 | xargs kill -9

# 또는 다른 포트 사용
flask run --port=5001
```

### 문제 4: CORS 오류
**증상**: 브라우저에서 `CORS policy` 오류

**해결**: `app/__init__.py`에서 CORS 설정 확인
```python
CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})
```

---

## 다음 단계

Phase 1 완료 후:
1. **PROGRESS.md 업데이트**: Phase 1 완료 기록
2. **Git 커밋**:
   ```bash
   git add .
   git commit -m "Phase 1: Initial project structure and dev environment setup"
   ```
3. **Phase 2로 이동**: [Phase 2: 데이터베이스 설계](./phase-02.md)

---

**완료 기준**:
- Frontend 개발 서버 정상 실행 (http://localhost:5173)
- Backend API 서버 정상 실행 (http://localhost:5000)
- Health check 엔드포인트 200 OK 응답
