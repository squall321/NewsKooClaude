# 빠른 시작 가이드

## Phase별 개발 시작 방법

### 현재 상태
- ✅ 프로젝트 기획 및 로드맵 완료
- 📝 다음 단계: Phase 1 시작

---

## Phase 1 시작하기: 프로젝트 구조 설정

### 목표
- 프론트엔드 (React + Vite + TypeScript) 초기 설정
- 백엔드 (Flask) 초기 설정
- 개발 환경 구성

### 단계별 가이드

#### 1. Frontend 설정

```bash
# Vite로 React + TypeScript 프로젝트 생성
npm create vite@latest frontend -- --template react-ts

cd frontend
npm install

# 추가 의존성 설치
npm install react-router-dom
npm install @tanstack/react-query
npm install axios
npm install styled-components
npm install @types/styled-components -D

# 개발 도구
npm install -D eslint prettier
npm install -D @typescript-eslint/eslint-plugin @typescript-eslint/parser
```

**frontend/.eslintrc.json 생성**:
```json
{
  "extends": [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:react-hooks/recommended"
  ],
  "parser": "@typescript-eslint/parser",
  "plugins": ["@typescript-eslint", "react-refresh"],
  "rules": {
    "react-refresh/only-export-components": "warn"
  }
}
```

**frontend/.prettierrc 생성**:
```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 80,
  "tabWidth": 2
}
```

**frontend/.env.example**:
```env
VITE_API_URL=http://localhost:5000/api/v1
```

#### 2. Backend 설정

```bash
# Backend 디렉토리 생성
mkdir backend
cd backend

# Python 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Flask 및 필수 패키지 설치
pip install flask flask-cors flask-sqlalchemy
pip install python-dotenv
pip install alembic
pip install psycopg2-binary
pip install redis
pip install celery

# 개발 도구
pip install black flake8 pytest

# requirements.txt 생성
pip freeze > requirements.txt
```

**backend/.env.example**:
```env
FLASK_APP=app
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-in-production
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/humorhub
REDIS_URL=redis://localhost:6379/0

# API Keys (나중에 추가)
OPENAI_API_KEY=
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=
DEEPL_API_KEY=
```

**backend/app/__init__.py**:
```python
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(app)
    db.init_app(app)

    # Blueprint 등록 (나중에 추가)

    return app
```

**backend/config.py**:
```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URL = os.environ.get('REDIS_URL')
```

**backend/run.py**:
```python
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

#### 3. Docker Compose 설정

**docker-compose.yml** (프로젝트 루트):
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14-alpine
    environment:
      POSTGRES_DB: humorhub
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    command: python run.py
    volumes:
      - ./backend:/app
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/humorhub
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis

  frontend:
    build: ./frontend
    command: npm run dev -- --host
    volumes:
      - ./frontend:/app
      - /app/node_modules
    ports:
      - "5173:5173"
    environment:
      - VITE_API_URL=http://localhost:5000/api/v1

volumes:
  postgres_data:
```

**backend/Dockerfile**:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "run.py"]
```

**frontend/Dockerfile**:
```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json .
RUN npm install

COPY . .

CMD ["npm", "run", "dev"]
```

#### 4. Git 설정

**.gitignore** (프로젝트 루트):
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

# Node
node_modules/
dist/
build/

# Environment
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Database
*.db
*.sqlite

# Logs
*.log
logs/

# Docker
docker-compose.override.yml
```

#### 5. 디렉토리 구조 생성

```bash
# Backend structure
mkdir -p backend/app/{api,models,services,crawlers,translators,utils}
mkdir -p backend/migrations
mkdir -p backend/tests

# Frontend structure
mkdir -p frontend/src/{components,pages,hooks,api,styles,utils,types}
mkdir -p frontend/public
```

---

## Phase 1 완료 체크리스트

- [ ] Frontend Vite 프로젝트 생성 및 의존성 설치
- [ ] Backend Flask 프로젝트 구조 생성
- [ ] Docker Compose 설정
- [ ] 환경 변수 파일 (.env.example) 생성
- [ ] ESLint, Prettier 설정
- [ ] .gitignore 설정
- [ ] 디렉토리 구조 생성
- [ ] README.md 업데이트
- [ ] PROGRESS.md에 Phase 1 완료 기록

---

## 완료 후

Phase 1을 완료한 후:

1. **PROGRESS.md 업데이트**:
```markdown
## Phase 1: 프로젝트 구조 및 개발 환경 설정
**완료 날짜**: 2025-11-XX
**소요 시간**: X시간

### 구현 내용
- [x] Vite + React + TypeScript 프로젝트 생성
- [x] Flask 프로젝트 구조 생성
- [x] Docker Compose 설정
...
```

2. **Git 커밋**:
```bash
git add .
git commit -m "Phase 1: Initial project structure and development environment setup"
git push origin claude/humor-translation-platform-setup-018DSsL67aVjvbQMfYvNKhWX
```

3. **다음 Phase 준비**:
- Phase 2 체크리스트 검토
- 필요한 기술 학습
- API 키 준비 (OpenAI, Reddit 등)

---

## 개발 팁

### 개발 서버 실행

**Docker 사용**:
```bash
docker-compose up
```

**로컬 개발**:
```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
python run.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### 데이터베이스 마이그레이션

```bash
cd backend
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 코드 포맷팅

```bash
# Backend
black backend/
flake8 backend/

# Frontend
cd frontend
npm run lint
npm run format
```

---

## 문제 해결

### Port already in use
```bash
# 프로세스 종료
lsof -ti:5000 | xargs kill -9  # Backend
lsof -ti:5173 | xargs kill -9  # Frontend
```

### Docker 볼륨 초기화
```bash
docker-compose down -v
docker-compose up -d
```

### Python 패키지 문제
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

---

**준비되셨나요?** Phase 1을 시작하세요! 🚀
