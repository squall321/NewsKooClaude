# 국제 유머 번역 플랫폼 (HumorHub)

> 전 세계의 유머를 한국어로 번역하여 전달하는 자동화 플랫폼

## 프로젝트 비전

Reddit, Twitter 등 해외 커뮤니티의 다양한 업계별 유머 콘텐츠를 자동으로 크롤링하고 AI 번역하여, 한국 사용자들이 쉽게 즐길 수 있도록 서비스합니다. 검수 시스템을 통해 번역 품질을 보장하며, 직관적인 UX로 모바일과 데스크탑에서 최적의 경험을 제공합니다.

## 주요 기능

### 자동화 시스템
- **자동 크롤링**: Reddit, Twitter, 9GAG 등 다양한 소스에서 유머 콘텐츠 수집
- **AI 번역**: GPT/DeepL API를 활용한 자연스러운 한국어 번역
- **스마트 분류**: AI 기반 자동 카테고리 및 태그 생성
- **이미지 처리**: OCR 텍스트 추출 및 번역, 이미지 최적화

### 검수 및 관리
- **검수 대시보드**: 번역된 콘텐츠를 쉽게 검토하고 수정
- **수동 업로드**: 직접 발견한 유머를 간편하게 추가
- **콘텐츠 필터링**: NSFW, 스팸, 저품질 콘텐츠 자동 필터링
- **통계 대시보드**: 수집, 번역, 조회 통계 실시간 모니터링

### 사용자 경험
- **반응형 디자인**: 모바일/데스크탑 최적화 UI
- **다크모드**: 눈의 피로를 줄이는 테마 지원
- **무한 스크롤**: 끊김 없는 콘텐츠 탐색
- **카테고리별 탐색**: IT, 의료, 교육, 직장 등 업계별 분류
- **검색**: 빠른 콘텐츠 검색 기능
- **공유**: SNS 공유 최적화

### 수익화
- **Google AdSense**: 전략적 광고 배치로 수익 창출
- **모바일 앱**: React Native 기반 Android/iOS 앱

## 기술 스택

### Frontend
- **React 18** + **TypeScript**
- **Vite** (빌드 도구)
- **Styled Components** / **Emotion** (CSS-in-JS)
- **React Router** (라우팅)
- **Framer Motion** (애니메이션)
- **React Query** (데이터 페칭)

### Backend
- **Flask** (Python)
- **SQLAlchemy** (ORM)
- **PostgreSQL** (데이터베이스)
- **Redis** (캐싱, 작업 큐)
- **Celery** (백그라운드 작업)

### 크롤링 & 번역
- **PRAW** (Reddit API)
- **OpenAI GPT-4** (번역)
- **DeepL API** (번역 대체)
- **Tesseract** (OCR)
- **Beautiful Soup** (웹 스크래핑)

### 인프라
- **Docker** + **Docker Compose**
- **Nginx** (리버스 프록시)
- **GitHub Actions** (CI/CD)
- **AWS S3** / **Cloudflare R2** (이미지 스토리지)
- **Let's Encrypt** (SSL)

## 프로젝트 구조

```
NewsKooClaude/
├── frontend/                # React 프론트엔드
│   ├── src/
│   │   ├── components/     # 재사용 컴포넌트
│   │   ├── pages/          # 페이지 컴포넌트
│   │   ├── hooks/          # 커스텀 훅
│   │   ├── api/            # API 클라이언트
│   │   ├── styles/         # 글로벌 스타일
│   │   └── utils/          # 유틸리티 함수
│   ├── public/
│   └── package.json
├── backend/                 # Flask 백엔드
│   ├── app/
│   │   ├── api/            # API 엔드포인트
│   │   ├── models/         # 데이터베이스 모델
│   │   ├── services/       # 비즈니스 로직
│   │   ├── crawlers/       # 크롤러 모듈
│   │   ├── translators/    # 번역 서비스
│   │   └── utils/          # 유틸리티
│   ├── migrations/         # DB 마이그레이션
│   ├── tests/
│   └── requirements.txt
├── docker-compose.yml       # 개발 환경
├── DEVELOPMENT_ROADMAP.md   # 개발 로드맵 (50 Phases)
├── PROGRESS.md              # 진행 상황 추적
└── README.md
```

## 개발 로드맵

전체 개발은 **50개 Phase**로 나뉘어 있습니다. 자세한 내용은 [DEVELOPMENT_ROADMAP.md](./DEVELOPMENT_ROADMAP.md)를 참조하세요.

### Phase 개요
- **Phase 1-10**: 프로젝트 초기 설정 및 기반 구축
- **Phase 11-20**: 크롤링 및 번역 시스템
- **Phase 21-30**: 관리자 대시보드
- **Phase 31-40**: 사용자 프론트엔드 및 UX
- **Phase 41-50**: 배포, 최적화, 모바일 앱

**현재 진행**: Phase 0 (계획 수립 완료)

진행 상황은 [PROGRESS.md](./PROGRESS.md)에서 확인할 수 있습니다.

## 시작하기

### 필수 요구사항
- Node.js 18+
- Python 3.10+
- Docker & Docker Compose
- PostgreSQL 14+
- Redis

### 환경 설정

1. **레포지토리 클론**
```bash
git clone https://github.com/squall321/NewsKooClaude.git
cd NewsKooClaude
```

2. **환경 변수 설정**
```bash
# Backend
cp backend/.env.example backend/.env
# Frontend
cp frontend/.env.example frontend/.env
```

필요한 API 키 설정:
- OpenAI API Key
- Reddit API Credentials
- DeepL API Key (선택)

3. **Docker로 실행**
```bash
docker-compose up -d
```

4. **로컬 개발 (Docker 미사용)**

Backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
flask db upgrade
flask run
```

Frontend:
```bash
cd frontend
npm install
npm run dev
```

### 접속
- Frontend: http://localhost:5173
- Backend API: http://localhost:5000
- Admin Dashboard: http://localhost:5173/admin

## 기여하기

이 프로젝트는 현재 개인 프로젝트이지만, 기여를 환영합니다!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.

## 연락처

프로젝트 관련 문의: [GitHub Issues](https://github.com/squall321/NewsKooClaude/issues)

---

**개발 시작일**: 2025-11-15
**목표 런칭일**: 2025년 Q2
