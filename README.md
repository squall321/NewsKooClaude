# 국제 유머 각색 플랫폼 (HumorHub Korea)

> 전 세계의 유머를 한국식으로 재해석하여 전달하는 **제로 비용** 자동화 플랫폼

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/react-18.0+-61dafb.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/typescript-5.0+-blue.svg)](https://www.typescriptlang.org/)

## 프로젝트 비전

Reddit, Twitter 등 해외 커뮤니티의 유머 콘텐츠를 **단순 번역이 아닌 재창작/각색**하여, 한국 독자들에게 자연스럽고 재미있게 전달합니다. 로컬 GPU를 활용한 AI 보조 작성으로 **API 비용 제로**, 검수 시스템으로 품질 보장, 모바일/데스크탑 최적화 UX로 최고의 읽기 경험을 제공합니다.

### 왜 "번역"이 아니라 "각색"인가?

1. **법적 안전성**: Reddit 약관 준수, Fair Use 원칙 적용
2. **문화적 맥락**: 한국 독자가 이해하기 쉽게 재해석
3. **유머 보존**: 직역으로 잃어버리는 웃음 포인트 유지
4. **창작물로서 가치**: 원본의 아이디어만 차용한 독립적 콘텐츠

## 핵심 차별점

### 💰 제로 비용 운영
- **로컬 LLM**: RTX 5070 TI (16GB VRAM)로 HuggingFace 모델 실행
- **API 비용 없음**: OpenAI, DeepL 등 유료 서비스 제거
- **자체 호스팅**: 저렴한 VPS 또는 Oracle Cloud Free Tier
- **로컬 스토리지**: 이미지는 파일 시스템에 직접 저장

**월 운영 비용**: **$5-10** (API 기반 대비 90% 절감)

### 🤖 AI 보조 창작 시스템
- **수동 우선**: 작성자가 직접 쓰는 것이 기본
- **AI는 도구**: 초안 제안, 스타일 개선, 제목 생성 보조
- **품질 보장**: 원본 유사도 70% 이하 유지 (표절 방지)
- **Few-shot Learning**: 블로그 스타일 예시 학습

### ⚖️ 법적 준수
- 원본 본문 저장 안 함 (메타데이터만)
- 재구성된 콘텐츠는 독립적 창작물
- 원본 출처 명시 (Reddit 링크)
- Transformative Use (상업적 이용 전 변환)

### 📱 모바일 우선 UX
- 반응형 디자인
- 다크모드 지원
- 무한 스크롤
- PWA 지원 (앱처럼 사용)

## 주요 기능

### 작성자용 (관리 대시보드)
- **영감 소스 관리**: Reddit에서 수집한 유머 아이디어 탐색
- **AI 재구성 도우미**:
  - 원본 → 3-5개 버전 재창작
  - 스타일 선택 (캐주얼/격식/유머러스)
  - 제목 제안, 문단 개선
- **마크다운 에디터**: 실시간 미리보기, 자동 저장
- **이미지 관리**: 로컬 업로드, WebP 자동 변환
- **블로그 스타일 가이드**: 일관된 톤앤매너 유지

### 독자용 (사용자 페이지)
- **깔끔한 피드**: 카드 기반 무한 스크롤
- **카테고리별 탐색**: IT/개발, 의료, 직장, 일상 등
- **검색 & 필터**: 빠른 콘텐츠 찾기
- **공유 최적화**: 카카오톡, SNS 공유
- **다크모드**: 눈 편한 읽기

### 자동화 시스템
- **스케줄 크롤링**: 일일 1-2회 Reddit 모니터링
- **자동 필터링**: NSFW, 스팸, 저품질 콘텐츠 제거
- **SEO 최적화**: 검색 엔진 노출 극대화

## 기술 스택

### Frontend
```
React 18 + TypeScript + Vite
Tailwind CSS / styled-components
React Router (라우팅)
Framer Motion (애니메이션)
React Query (데이터 페칭)
```

### Backend
```
Flask (Python 3.10+)
SQLAlchemy ORM
SQLite (개발) → PostgreSQL (프로덕션)
Redis (캐싱, 선택적)
APScheduler (크롤링 스케줄러)
```

### AI/LLM (로컬)
```
HuggingFace Transformers
vLLM (빠른 추론 엔진)
추천 모델: EEVE-Korean-10.8B (INT8 양자화)
CUDA 12.x + PyTorch 2.x
```

### 크롤링 & 데이터
```
PRAW (Reddit API)
BeautifulSoup (웹 스크래핑)
Pillow (이미지 처리)
```

### 인프라
```
Docker + Docker Compose
Nginx (리버스 프록시)
GitHub Actions (CI/CD)
Let's Encrypt (SSL)
Contabo VPS / Oracle Cloud Free Tier
```

## 프로젝트 구조

```
NewsKooClaude/
├── frontend/                     # React 프론트엔드
│   ├── src/
│   │   ├── components/          # UI 컴포넌트
│   │   │   ├── common/          # Button, Card, Modal 등
│   │   │   ├── post/            # 게시물 관련
│   │   │   └── admin/           # 관리자 전용
│   │   ├── pages/               # 페이지
│   │   │   ├── Home.tsx
│   │   │   ├── PostDetail.tsx
│   │   │   ├── Category.tsx
│   │   │   └── admin/           # 관리자 페이지
│   │   ├── hooks/               # 커스텀 훅
│   │   ├── api/                 # API 클라이언트
│   │   ├── styles/              # 디자인 시스템
│   │   ├── utils/               # 유틸리티
│   │   └── types/               # TypeScript 타입
│   └── package.json
│
├── backend/                      # Flask 백엔드
│   ├── app/
│   │   ├── __init__.py
│   │   ├── api/                 # API 엔드포인트
│   │   │   ├── posts.py
│   │   │   ├── drafts.py
│   │   │   ├── inspirations.py
│   │   │   └── ai_assistant.py
│   │   ├── models/              # DB 모델
│   │   │   ├── post.py
│   │   │   ├── draft.py
│   │   │   ├── inspiration.py
│   │   │   └── user.py
│   │   ├── services/            # 비즈니스 로직
│   │   │   ├── ai_rewriter.py   # AI 재구성 엔진
│   │   │   ├── crawler.py       # Reddit 크롤러
│   │   │   └── image_processor.py
│   │   ├── llm/                 # 로컬 LLM 관리
│   │   │   ├── model_loader.py
│   │   │   ├── prompts.py       # 프롬프트 템플릿
│   │   │   └── inference.py
│   │   └── utils/
│   ├── migrations/              # DB 마이그레이션
│   ├── static/uploads/          # 업로드된 이미지
│   ├── tests/
│   ├── requirements.txt
│   └── run.py
│
├── docs/                         # 문서
│   ├── DEVELOPMENT_ROADMAP.md   # 50 Phase 로드맵
│   ├── PROGRESS.md              # 진행 상황 추적
│   ├── QUICK_START_GUIDE.md     # 빠른 시작 가이드
│   └── LOCAL_LLM_SETUP.md       # 로컬 LLM 설정 가이드
│
├── docker-compose.yml            # 개발 환경
├── .gitignore
└── README.md
```

## 빠른 시작

### 필수 요구사항

#### 하드웨어
- **GPU**: NVIDIA RTX 5070 TI (16GB VRAM) 또는 유사
- **RAM**: 16GB+ 권장
- **저장공간**: 50GB+ (모델 + 데이터)

#### 소프트웨어
- **Python** 3.10+
- **Node.js** 18+
- **CUDA** 12.x
- **Docker** & **Docker Compose** (선택적)

### 설치 단계

#### 1. 레포지토리 클론
```bash
git clone https://github.com/squall321/NewsKooClaude.git
cd NewsKooClaude
```

#### 2. 환경 변수 설정
```bash
# Backend
cp backend/.env.example backend/.env

# Frontend
cp frontend/.env.example frontend/.env
```

**backend/.env** 필수 설정:
```env
# 데이터베이스
DATABASE_URL=sqlite:///humorhub.db

# Reddit API
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=HumorHub/1.0

# 로컬 LLM 설정
LLM_MODEL_NAME=EEVE-Korean-10.8B-v1.0
LLM_MODEL_PATH=/path/to/models/
LLM_DEVICE=cuda  # 또는 cpu
LLM_QUANTIZATION=int8  # vram 절약

# Flask
SECRET_KEY=change-this-in-production
```

#### 3. 로컬 LLM 모델 다운로드 (중요!)

**추천 모델**: EEVE-Korean-10.8B (INT8 양자화)

```bash
cd backend

# HuggingFace CLI 설치
pip install huggingface-hub

# 모델 다운로드 (14GB, 약 20분 소요)
huggingface-cli download yanolja/EEVE-Korean-10.8B-v1.0 \
  --local-dir ./models/EEVE-Korean-10.8B

# 양자화 (선택적, VRAM 절약)
python scripts/quantize_model.py --model EEVE-Korean-10.8B
```

자세한 가이드: [LOCAL_LLM_SETUP.md](./docs/LOCAL_LLM_SETUP.md)

#### 4-A. Docker로 실행 (권장)

```bash
docker-compose up -d
```

#### 4-B. 로컬 개발 (Docker 미사용)

**Backend**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# DB 초기화
flask db upgrade

# 개발 서버 실행
python run.py
```

**Frontend**:
```bash
cd frontend
npm install
npm run dev
```

#### 5. 접속
- **사용자 페이지**: http://localhost:5173
- **관리 대시보드**: http://localhost:5173/admin
- **Backend API**: http://localhost:5000

## 개발 로드맵

전체 개발은 **50개 Phase**로 구성됩니다. 자세한 내용은 [DEVELOPMENT_ROADMAP.md](./DEVELOPMENT_ROADMAP.md)를 참조하세요.

### 주요 마일스톤

#### Phase 1-10: 기반 구축 (2-3주)
- ✅ 프로젝트 구조 설정
- 🔄 로컬 LLM 환경 구축 ⭐ **가장 중요**
- 데이터베이스 설계
- Reddit 크롤링 시스템
- AI 재구성 엔진

#### Phase 11-20: 관리 대시보드 (2-3주)
- 글 작성 에디터
- AI 보조 패널
- 영감 소스 탐색
- 이미지 관리
- 초안 & 게시물 관리

#### Phase 21-30: 사용자 UI (3-4주)
- 디자인 시스템
- 홈 피드 (무한 스크롤)
- 게시물 상세 페이지
- 카테고리/검색
- 다크모드

#### Phase 31-40: 고급 기능 (2주)
- 애니메이션
- PWA
- SEO 최적화
- Google AdSense
- 성능 최적화

#### Phase 41-50: 배포 & 운영 (2주)
- VPS 배포
- CI/CD
- 보안 강화
- 모니터링
- 문서화

**현재 진행**: Phase 0 (계획 수립 완료)

## 비용 구조

### 월간 운영 비용

| 항목 | 기존 방식 | 제로 비용 전략 | 절감액 |
|------|-----------|----------------|--------|
| 번역 API | $50-200 | **$0** (로컬 LLM) | -$100 |
| 서버 | $20-100 | **$0-5** (VPS) | -$50 |
| DB | $15-50 | **$0** (자체 호스팅) | -$30 |
| 스토리지 | $10-50 | **$0** (로컬 FS) | -$20 |
| 도메인 | $1/월 | **$1/월** | $0 |
| **총합** | **$96-401/월** | **$1-6/월** | **-90%+** |

**전기 비용**: RTX 5070 TI 하루 1시간 사용 시 월 $3-5 추가

## 성공 지표

### 3개월 목표
- ✅ 게시물 50개 발행
- ✅ 일일 활성 사용자 100명
- ✅ 페이지 로드 속도 < 1.5초
- ✅ 광고 수익 월 $20+
- ✅ AI 재구성 활용도 50%

### 6개월 목표
- 게시물 200개
- 일일 활성 사용자 500명
- 광고 수익 월 $100+
- SEO 트래픽 60%+
- 모바일 앱 출시 (React Native)

## Reddit 약관 준수

### Transformative Use 체크리스트
- ✅ 원본 본문 저장 안 함 (메타데이터만 수집)
- ✅ 재구성된 콘텐츠는 독립적 창작물 (유사도 < 70%)
- ✅ 원본 출처 명시 (Reddit 게시물 링크)
- ✅ Fair Use 원칙 준수 (교육적/변형적 이용)
- ✅ 상업적 이용 전 변환 (단순 복사가 아님)

**법적 자문**: 미국 저작권법 Fair Use 4요소 충족
1. **목적**: 교육적, 변형적 (재창작)
2. **원저작물의 성격**: 공개된 유머 (사실적 정보)
3. **이용된 부분**: 아이디어만 차용 (표현은 독창적)
4. **시장 영향**: 원본과 경쟁 관계 없음

## 기여하기

이 프로젝트는 현재 개인 프로젝트이지만, 기여를 환영합니다!

### 기여 방법
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### 개발 가이드
- [DEVELOPMENT_ROADMAP.md](./DEVELOPMENT_ROADMAP.md) - 전체 로드맵
- [PROGRESS.md](./PROGRESS.md) - 진행 상황 추적
- [LOCAL_LLM_SETUP.md](./docs/LOCAL_LLM_SETUP.md) - LLM 설정

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.

## 연락처

- **GitHub Issues**: [squall321/NewsKooClaude/issues](https://github.com/squall321/NewsKooClaude/issues)
- **프로젝트 Wiki**: 준비 중

---

**개발 시작일**: 2025-11-15
**목표 런칭일**: 2026년 Q1
**핵심 철학**: 💰 비용 제로 + ⚖️ 법적 준수 + 🤖 AI 보조 창작

---

### 추천 읽기 순서

1. **시작**: [README.md](./README.md) (여기)
2. **로드맵**: [DEVELOPMENT_ROADMAP.md](./DEVELOPMENT_ROADMAP.md)
3. **빠른 시작**: [QUICK_START_GUIDE.md](./QUICK_START_GUIDE.md)
4. **LLM 설정**: [LOCAL_LLM_SETUP.md](./docs/LOCAL_LLM_SETUP.md) ⭐
5. **진행 추적**: [PROGRESS.md](./PROGRESS.md)

**지금 바로 시작하세요!** 🚀
