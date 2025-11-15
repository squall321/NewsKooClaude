# Phase 1 구현 상세 문서

**Phase**: 프로젝트 구조 및 개발 환경 설정
**완료 날짜**: 2025-11-15
**소요 시간**: 약 2시간

---

## 📋 개요

Phase 1에서는 NewsKoo 프로젝트의 기본 구조를 설정하고 개발 환경을 구축했습니다. 프론트엔드(React + TypeScript + Vite)와 백엔드(Flask) 프로젝트를 생성하고, 필수 도구들을 설정했습니다.

---

## 🎯 달성 목표

- ✅ Vite 기반 React + TypeScript 프론트엔드 프로젝트 생성
- ✅ Flask 백엔드 프로젝트 구조 설계 및 구현
- ✅ 코드 품질 도구 설정 (ESLint, Prettier)
- ✅ 환경변수 관리 시스템 구축
- ✅ 전체 프로젝트 디렉토리 구조 확립
- ✅ 개발 문서 작성

---

## 📂 생성된 디렉토리 구조

```
NewsKooClaude/
├── frontend/                      # React 프론트엔드
│   ├── src/
│   │   ├── components/           # 재사용 컴포넌트
│   │   │   ├── common/
│   │   │   ├── layout/
│   │   │   ├── post/
│   │   │   ├── admin/
│   │   │   └── ui/
│   │   ├── pages/                # 페이지 컴포넌트
│   │   ├── hooks/                # Custom Hooks
│   │   ├── services/             # API 서비스
│   │   ├── types/                # TypeScript 타입
│   │   ├── contexts/             # React Context
│   │   ├── utils/                # 유틸리티
│   │   ├── styles/               # 스타일
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── public/
│   ├── index.html
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.js        # Tailwind 설정
│   ├── postcss.config.js
│   ├── eslint.config.js          # ESLint 설정
│   ├── .prettierrc               # Prettier 설정
│   ├── .env.example
│   ├── package.json
│   └── README.md
│
├── backend/                       # Flask 백엔드
│   ├── app/
│   │   ├── __init__.py           # Flask 앱 팩토리
│   │   ├── api/                  # API 라우트
│   │   │   └── __init__.py
│   │   ├── models/               # DB 모델
│   │   ├── services/             # 비즈니스 로직
│   │   ├── utils/                # 유틸리티
│   │   └── config/               # 설정
│   │       └── __init__.py
│   ├── tests/                    # 테스트
│   ├── scripts/                  # 유틸리티 스크립트
│   ├── run.py                    # 실행 파일
│   ├── requirements.txt          # Python 의존성
│   └── README.md
│
├── docs/                          # 프로젝트 문서
│   ├── phases/                   # Phase별 가이드
│   ├── implementation/           # 구현 상세 문서
│   ├── PHASE_INDEX.md
│   ├── LOCAL_LLM_SETUP.md
│   └── ...
│
├── .gitignore
├── .env.example                  # 환경변수 템플릿
├── DEVELOPMENT_ROADMAP.md
├── PROGRESS.md
├── README.md
└── QUICK_START_GUIDE.md
```

---

## 🔧 주요 구현 내용

### 1. 프론트엔드 프로젝트 설정

#### 1.1 Vite + React + TypeScript 프로젝트 생성

```bash
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
```

#### 1.2 필수 패키지 설치

```bash
npm install react-router-dom @tanstack/react-query axios
npm install -D tailwindcss postcss autoprefixer
npm install -D prettier eslint-config-prettier eslint-plugin-prettier
```

**설치된 주요 패키지**:
- `react-router-dom@6.x` - 클라이언트 라우팅
- `@tanstack/react-query@5.x` - 서버 상태 관리
- `axios@1.x` - HTTP 클라이언트
- `tailwindcss@3.x` - CSS 프레임워크

#### 1.3 Tailwind CSS 설정

**tailwind.config.js**:
```javascript
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          // ... 기타 색상
          900: '#0c4a6e',
        },
      },
    },
  },
  plugins: [],
}
```

**src/index.css**:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

/* 커스텀 컴포넌트 클래스 */
@layer components {
  .btn-primary {
    @apply bg-primary-600 hover:bg-primary-700 text-white
           font-medium py-2 px-4 rounded-lg transition-colors;
  }
  .card {
    @apply bg-white rounded-lg shadow-md p-6;
  }
}
```

#### 1.4 ESLint + Prettier 통합

**eslint.config.js**:
```javascript
import prettier from 'eslint-plugin-prettier'
import prettierConfig from 'eslint-config-prettier'

export default defineConfig([
  globalIgnores(['dist', 'node_modules']),
  {
    files: ['**/*.{ts,tsx,js,jsx}'],
    extends: [
      // ... 기존 설정
      prettierConfig,
    ],
    plugins: { prettier },
    rules: {
      'prettier/prettier': 'warn',
      '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
    },
  },
])
```

**.prettierrc**:
```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2,
  "useTabs": false
}
```

#### 1.5 디렉토리 구조 생성

```bash
mkdir -p src/{components,pages,hooks,utils,services,types,contexts,styles}
mkdir -p src/components/{common,layout,post,admin,ui}
```

---

### 2. 백엔드 프로젝트 설정

#### 2.1 Flask 앱 팩토리 패턴

**backend/app/__init__.py**:
```python
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_name='development'):
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(f'app.config.{config_name.capitalize()}Config')

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # CORS 설정
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config.get('CORS_ORIGINS', ['http://localhost:5173']),
            "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
        }
    })

    # Register blueprints
    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    return app
```

#### 2.2 환경별 설정 관리

**backend/app/config/__init__.py**:
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "NewsKoo"
    DEBUG: bool = False
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI: str = 'sqlite:///newskoo.db'
    JWT_SECRET_KEY: str = os.getenv('JWT_SECRET_KEY', 'jwt-secret')

    # LLM
    LLM_MODEL_NAME: str = 'yanolja/EEVE-Korean-10.8B-v1.0'
    LLM_DEVICE: str = 'cuda'

    class Config:
        env_file = '.env'

class DevelopmentConfig(Settings):
    DEBUG: bool = True
    SQLALCHEMY_DATABASE_URI: str = 'sqlite:///newskoo_dev.db'

class ProductionConfig(Settings):
    DEBUG: bool = False
    SQLALCHEMY_DATABASE_URI: str = os.getenv('DATABASE_URL', 'postgresql://...')
```

#### 2.3 API Blueprint 구조

**backend/app/api/__init__.py**:
```python
from flask import Blueprint

api_bp = Blueprint('api', __name__)

@api_bp.route('/ping')
def ping():
    return {'message': 'pong', 'version': '1.0.0'}, 200
```

#### 2.4 실행 스크립트

**backend/run.py**:
```python
import os
from app import create_app, db

config_name = os.getenv('FLASK_ENV', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])
```

---

### 3. 환경변수 관리

**루트 .env.example**:
```env
# Flask Backend
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key
PORT=5000

# Database
DATABASE_URL=sqlite:///newskoo_dev.db

# LLM Configuration
LLM_MODEL_NAME=yanolja/EEVE-Korean-10.8B-v1.0
LLM_DEVICE=cuda
LLM_MAX_LENGTH=2048
```

**frontend/.env.example**:
```env
VITE_API_BASE_URL=http://localhost:5000/api
VITE_APP_NAME=NewsKoo
```

---

### 4. Git 설정

**.gitignore**:
```gitignore
# Python
__pycache__/
*.pyc
venv/
*.db

# Frontend
frontend/node_modules/
frontend/dist/

# Environment
.env
.env.local

# LLM Models
*.bin
*.safetensors
models/
```

---

## ✅ 검증 및 테스트

### 프론트엔드 검증

```bash
cd frontend
npm run dev
```

**결과**: ✅ Vite 서버가 `http://localhost:5173`에서 성공적으로 시작

```
VITE v7.2.2  ready in 300 ms
➜  Local:   http://localhost:5173/
```

### 백엔드 검증

```bash
cd backend
python3 -m py_compile app/__init__.py app/config/__init__.py app/api/__init__.py run.py
```

**결과**: ✅ 모든 Python 파일 구문 검증 통과

---

## 📚 생성된 문서

1. **frontend/README.md** - 프론트엔드 설정 및 사용 가이드
2. **backend/README.md** - 백엔드 설정 및 API 문서
3. **frontend/src/components/README.md** - 컴포넌트 작성 가이드
4. **PROGRESS.md** - 개발 진행 상황 추적 (업데이트)

---

## 🔑 핵심 기술 결정

### Frontend
- **Build Tool**: Vite (빠른 HMR, 간단한 설정)
- **Styling**: Tailwind CSS (유틸리티 우선, 빠른 프로토타이핑)
- **State**: React Query (서버 상태 관리)
- **Routing**: React Router v6

### Backend
- **Framework**: Flask 3.0 (가벼움, 확장성)
- **ORM**: SQLAlchemy (타입 안전성)
- **Config**: Pydantic Settings (환경별 설정)
- **API**: Blueprint 패턴 (모듈화)

### 개발 도구
- **Linting**: ESLint + Prettier (코드 품질 일관성)
- **Type Safety**: TypeScript (프론트엔드)
- **Version Control**: Git + .gitignore

---

## 💡 배운 점

1. **Vite의 속도**: Create React App 대비 현저히 빠른 빌드 속도
2. **Tailwind의 생산성**: 유틸리티 클래스로 빠른 스타일링
3. **Flask 팩토리 패턴**: 테스트와 확장성에 유리한 구조
4. **Pydantic Settings**: 타입 안전한 환경변수 관리

---

## ⚠️ 문제 해결 사례

### 문제 1: npx tailwindcss init 실패
- **증상**: `npm error could not determine executable to run`
- **해결**: 수동으로 `tailwind.config.js`와 `postcss.config.js` 생성

### 문제 2: ESLint Flat Config
- **증상**: Prettier 통합 방법 변경
- **해결**: `eslint-plugin-prettier`와 `eslint-config-prettier`를 flat config 형식으로 import

---

## 📝 다음 단계 (Phase 2)

- [ ] 데이터베이스 모델 설계 (User, Post, Source, etc.)
- [ ] ERD 다이어그램 작성
- [ ] SQLAlchemy 모델 구현
- [ ] Flask-Migrate 설정
- [ ] 초기 Migration 생성

---

## 📊 Phase 1 통계

- **생성된 파일**: 약 30개
- **코드 라인**: 약 500줄
- **설치된 패키지**:
  - Frontend: 230개
  - Backend: 0개 (requirements.txt만 생성)
- **디렉토리**: 20+ 개

---

**Phase 1 완료 ✅**

다음: [Phase 2 - 데이터베이스 설계](./phase-02-implementation.md)
