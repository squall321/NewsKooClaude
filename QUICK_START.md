# 🚀 빠른 시작 가이드 (5분 설정)

NewsKoo 플랫폼을 로컬에서 실행하는 단계별 가이드입니다.

## 📋 목차

1. [사전 요구사항](#사전-요구사항)
2. [백엔드 설정](#백엔드-설정)
3. [프론트엔드 설정](#프론트엔드-설정)
4. [데이터베이스 초기화](#데이터베이스-초기화)
5. [실행](#실행)
6. [로그인 정보](#로그인-정보)
7. [문제 해결](#문제-해결)

---

## 사전 요구사항

### 필수 설치

- **Python 3.10+** ([다운로드](https://www.python.org/downloads/))
- **Node.js 18+** ([다운로드](https://nodejs.org/))
- **Git** ([다운로드](https://git-scm.com/))

### 선택 (GPU 사용 시)

- **CUDA 12.1+** (NVIDIA GPU 사용 시)
- **16GB+ VRAM** (로컬 LLM 사용 시)

---

## 백엔드 설정

### 1. 프로젝트 클론

```bash
git clone https://github.com/squall321/NewsKooClaude.git
cd NewsKooClaude/backend
```

### 2. 가상 환경 생성

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. 패키지 설치

```bash
pip install -r requirements.txt
```

> ⏱️ **예상 소요 시간**: 2-3분

### 4. 환경 변수 설정

루트 디렉토리에 `.env` 파일 생성:

```bash
cd ..
cp .env.example .env
```

`.env` 파일 편집 (최소 설정):

```env
# Database (SQLite - 개발용)
DATABASE_URL=sqlite:///newskoo.db

# Flask
SECRET_KEY=your-secret-key-change-this-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-this

# Reddit API (선택 - 크롤링 사용 시)
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=NewsKoo/1.0

# LLM 설정 (선택 - AI 기능 사용 시)
LLM_ENABLED=false  # GPU 없으면 false로 설정
LLM_MODEL_NAME=EEVE-Korean-10.8B-v1.0
LLM_DEVICE=cpu  # GPU 있으면 'cuda'
```

**시크릿 키 생성 방법:**

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 프론트엔드 설정

### 1. 디렉토리 이동

```bash
cd frontend
```

### 2. 패키지 설치

```bash
npm install
```

> ⏱️ **예상 소요 시간**: 1-2분

### 3. 환경 변수 설정

`frontend/.env` 파일 생성:

```bash
cp .env.example .env
```

내용:

```env
VITE_API_URL=http://localhost:5000
```

---

## 데이터베이스 초기화

### 1. 데이터베이스 생성

```bash
cd ../backend
python scripts/init_db.py
```

출력 예시:
```
🚀 데이터베이스 초기화 시작...
📁 마이그레이션 디렉토리 생성 중...
✅ 마이그레이션 디렉토리 생성 완료
📦 모델 로딩 중...
✅ 모델 로딩 완료
...
✅ 총 8개 테이블 생성됨
🎉 데이터베이스 초기화 완료!
```

### 2. 데모 데이터 생성

```bash
python scripts/seed_demo_data.py
```

출력 예시:
```
🌱 데모 데이터 시드 시작
👤 사용자 생성 중...
  ✅ admin (admin)
  ✅ editor (editor)
📂 카테고리 생성 중...
  ✅ IT/개발
  ✅ 의료/건강
  ...
✅ 데모 데이터 시드 완료!

📊 생성된 데이터:
  - 사용자: 2명
  - 카테고리: 6개
  - 태그: 12개
  - 게시물: 5개
```

---

## 실행

### 터미널 1: 백엔드 실행

```bash
cd backend
python run.py
```

출력:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

### 터미널 2: 프론트엔드 실행

```bash
cd frontend
npm run dev
```

출력:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

### 3. 브라우저에서 확인

🌐 **사용자 페이지**: http://localhost:5173
🔧 **관리자 페이지**: http://localhost:5173/admin
🔌 **API 문서**: http://localhost:5000/health

---

## 로그인 정보

### 관리자 계정
- **이메일**: `admin@newskoo.com`
- **비밀번호**: `admin123`
- **권한**: 모든 기능 접근 가능

### 에디터 계정
- **이메일**: `editor@newskoo.com`
- **비밀번호**: `editor123`
- **권한**: 게시물 작성/편집

---

## 문제 해결

### ❌ "ModuleNotFoundError: No module named 'flask'"

**원인**: 가상 환경이 활성화되지 않았거나 패키지 미설치

**해결**:
```bash
# 가상 환경 활성화 확인
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# 패키지 재설치
pip install -r requirements.txt
```

---

### ❌ "npm: command not found"

**원인**: Node.js가 설치되지 않음

**해결**: [Node.js 공식 사이트](https://nodejs.org/)에서 다운로드

---

### ❌ "Port 5000 is already in use"

**원인**: 5000 포트가 이미 사용 중

**해결**:
```bash
# 포트 사용 프로세스 확인
lsof -i :5000  # macOS/Linux
netstat -ano | findstr :5000  # Windows

# 또는 다른 포트 사용
export FLASK_RUN_PORT=5001
python run.py
```

---

### ❌ "Database locked" 에러

**원인**: SQLite 동시 접근 제한

**해결**:
```bash
# 데이터베이스 리셋
cd backend
python scripts/init_db.py --reset
```

---

### ❌ 프론트엔드 빌드 에러

**원인**: Node 모듈 충돌 또는 캐시 문제

**해결**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

---

### ❌ CORS 에러

**원인**: 백엔드 CORS 설정 문제

**해결**: `.env` 파일 확인
```env
FLASK_ENV=development
```

---

## 추가 설정 (선택)

### Reddit API 키 발급

1. https://www.reddit.com/prefs/apps 접속
2. "create application" 클릭
3. "script" 타입 선택
4. Client ID, Secret 복사
5. `.env`에 추가

### 로컬 LLM 설정

**GPU 있는 경우:**

```bash
cd backend
python scripts/download_model.py
```

`.env` 설정:
```env
LLM_ENABLED=true
LLM_DEVICE=cuda
```

**GPU 없는 경우:**

대안으로 OpenAI API 사용 권장:
```env
LLM_ENABLED=false
OPENAI_API_KEY=your-openai-api-key
```

---

## 다음 단계

✅ 설정 완료!

이제 다음을 시도해보세요:

1. **관리자 대시보드 탐색** (http://localhost:5173/admin)
2. **첫 게시물 작성**
3. **AI 보조 작성 기능 테스트** (LLM 활성화 시)
4. **카테고리/태그 관리**
5. **사용자 페이지 확인**

---

## 개발 모드 팁

### Hot Reload 활용

- **백엔드**: 코드 변경 시 자동 재시작
- **프론트엔드**: Vite HMR로 즉시 반영

### 데이터베이스 리셋

```bash
cd backend
python scripts/init_db.py --reset
python scripts/seed_demo_data.py
```

### 로그 확인

**백엔드**:
```bash
tail -f backend/logs/app.log
```

**프론트엔드**:
- 브라우저 개발자 도구 (F12) → Console

---

## 프로덕션 배포

프로덕션 배포는 [DEPLOYMENT.md](./docs/DEPLOYMENT.md) 참조

간단 배포:
```bash
docker-compose up -d
```

---

## 도움말

- **전체 문서**: [README.md](./README.md)
- **개발 로드맵**: [DEVELOPMENT_ROADMAP.md](./DEVELOPMENT_ROADMAP.md)
- **진행 상황**: [PROGRESS.md](./PROGRESS.md)
- **이슈 리포트**: [GitHub Issues](https://github.com/squall321/NewsKooClaude/issues)

---

**즐거운 개발 되세요!** 🎉
