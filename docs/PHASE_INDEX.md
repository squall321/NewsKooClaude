# Phase별 상세 가이드 인덱스

> 50개 Phase를 별도 md 파일로 관리하여 체계적인 개발 진행

## 사용 방법

1. 현재 진행 중인 Phase 파일을 엽니다
2. 상세 가이드를 따라 구현합니다
3. 완료 체크리스트를 확인합니다
4. PROGRESS.md에 완료 내용을 기록합니다
5. 다음 Phase로 이동합니다

---

## Phase 1-10: 프로젝트 초기 설정 및 기반 구축

### ✅ Phase 1: 프로젝트 구조 및 개발 환경 설정
- **파일**: [phase-01.md](./phases/phase-01.md)
- **난이도**: ⭐⭐☆☆☆
- **소요 시간**: 2-3시간
- **우선순위**: P0 (필수)
- **주요 내용**:
  - Vite + React + TypeScript 프로젝트 생성
  - Flask 프로젝트 구조 생성
  - ESLint, Prettier 설정
  - 디렉토리 구조 설계
  - 개발 서버 실행 테스트

### ✅ Phase 2: 데이터베이스 설계 및 모델 정의
- **파일**: [phase-02.md](./phases/phase-02.md)
- **난이도**: ⭐⭐⭐☆☆
- **소요 시간**: 3-4시간
- **우선순위**: P0 (필수)
- **주요 내용**:
  - ERD 설계 (재창작 철학 반영)
  - SQLAlchemy 모델 (User, Post, Category, Tag, Inspiration, Draft, WritingStyle)
  - Flask-Migrate 설정
  - 초기 데이터 시드

### 📝 Phase 3: Flask 기본 API 구조
- **파일**: [phase-03.md](./phases/phase-03.md)
- **난이도**: ⭐⭐⭐☆☆
- **소요 시간**: 2-3시간
- **우선순위**: P0 (필수)
- **주요 내용**:
  - Flask Blueprint 설계
  - RESTful API 엔드포인트 구조
  - CORS 설정
  - Error handling middleware
  - Logging 설정

### 📝 Phase 4: 인증 시스템 (관리자용)
- **파일**: [phase-04.md](./phases/phase-04.md)
- **난이도**: ⭐⭐⭐☆☆
- **소요 시간**: 2-3시간
- **우선순위**: P0 (필수)
- **주요 내용**:
  - JWT 토큰 기반 인증
  - Login/Refresh API
  - Protected route decorator
  - User CRUD API

### ✅ Phase 5: 로컬 LLM 환경 구축 ⭐ **가장 중요**
- **파일**: [phase-05.md](./phases/phase-05.md)
- **난이도**: ⭐⭐⭐⭐⭐
- **소요 시간**: 4-6시간
- **우선순위**: P0 (필수)
- **주요 내용**:
  - CUDA Toolkit 12.1 설치
  - PyTorch + CUDA 설정
  - EEVE-Korean-10.8B 다운로드 (14GB)
  - INT8 양자화 (VRAM 절약)
  - LLMModelLoader 구현
  - 추론 테스트

### 📝 Phase 6: AI 재구성 엔진 - 프롬프트 설계
- **파일**: [phase-06.md](./phases/phase-06.md)
- **난이도**: ⭐⭐⭐⭐☆
- **소요 시간**: 3-4시간
- **우선순위**: P1 (중요)
- **주요 내용**:
  - 프롬프트 템플릿 시스템
  - Few-shot examples 데이터베이스
  - 재구성 품질 평가 (유사도 체크)
  - 스타일별 프롬프트 (캐주얼/격식/유머러스)

### 📝 Phase 7: Reddit 영감 수집 시스템
- **파일**: [phase-07.md](./phases/phase-07.md)
- **난이도**: ⭐⭐⭐☆☆
- **소요 시간**: 2-3시간
- **우선순위**: P1 (중요)
- **주요 내용**:
  - PRAW (Reddit API) 설정
  - Subreddit 모니터링
  - 메타데이터만 수집 (본문 저장 안 함)
  - 인기도 기반 필터링

### 📝 Phase 8: 크롤링 스케줄러
- **파일**: [phase-08.md](./phases/phase-08.md)
- **난이도**: ⭐⭐⭐☆☆
- **소요 시간**: 2시간
- **우선순위**: P1 (중요)
- **주요 내용**:
  - APScheduler 통합
  - 일일 1-2회 자동 크롤링
  - 실패 재시도 로직
  - 크롤링 상태 모니터링 API

### 📝 Phase 9: 수동 작성 우선 시스템
- **파일**: [phase-09.md](./phases/phase-09.md)
- **난이도**: ⭐⭐⭐☆☆
- **소요 시간**: 3-4시간
- **우선순위**: P0 (필수)
- **주요 내용**:
  - Draft CRUD API
  - 마크다운 에디터 백엔드
  - 이미지 업로드 (로컬 저장)
  - 자동 저장 메커니즘
  - 발행/예약 발행 API

### 📝 Phase 10: AI 보조 작성 인터페이스
- **파일**: [phase-10.md](./phases/phase-10.md)
- **난이도**: ⭐⭐⭐⭐☆
- **소요 시간**: 3-4시간
- **우선순위**: P0 (필수)
- **주요 내용**:
  - AI 재구성 API (`/api/v1/ai/rewrite`)
  - 여러 버전 생성 (3-5개)
  - 원본 유사도 경고 시스템
  - 문단 개선 API
  - 제목 생성 API

---

## Phase 11-20: 관리자 대시보드 (작성 중심)

### 📝 Phase 11: 관리자 레이아웃
- **파일**: [phase-11.md](./phases/phase-11.md)
- **우선순위**: P0
- **주요 내용**: React Router, 사이드바, Protected routes

### 📝 Phase 12: 영감 소스 관리 대시보드
- **파일**: [phase-12.md](./phases/phase-12.md)
- **우선순위**: P1
- **주요 내용**: Reddit 게시물 탐색, 필터/정렬, 북마크

### 📝 Phase 13: 글 작성 에디터
- **파일**: [phase-13.md](./phases/phase-13.md)
- **우선순위**: P0
- **주요 내용**: 마크다운 에디터, 실시간 미리보기, 자동 저장

### 📝 Phase 14: AI 보조 작성 패널
- **파일**: [phase-14.md](./phases/phase-14.md)
- **우선순위**: P1
- **주요 내용**: 사이드 패널 AI 도우미, 재구성/개선/제목 제안

### 📝 Phase 15: 초안 관리
- **파일**: [phase-15.md](./phases/phase-15.md)
- **우선순위**: P1
- **주요 내용**: 초안 목록, 상태 관리, 초안 → 발행

### 📝 Phase 16: 게시물 관리
- **파일**: [phase-16.md](./phases/phase-16.md)
- **우선순위**: P1
- **주요 내용**: 게시물 CRUD, 통계, 비공개 전환

### 📝 Phase 17: 블로그 스타일 가이드 설정
- **파일**: [phase-17.md](./phases/phase-17.md)
- **우선순위**: P1
- **주요 내용**: 스타일 가이드 UI, Few-shot examples 업로드

### 📝 Phase 18: 이미지 관리
- **파일**: [phase-18.md](./phases/phase-18.md)
- **우선순위**: P1
- **주요 내용**: 로컬 이미지 업로드, WebP 변환, 이미지 라이브러리

### 📝 Phase 19: 카테고리/태그 관리
- **파일**: [phase-19.md](./phases/phase-19.md)
- **우선순위**: P1
- **주요 내용**: 카테고리 CRUD, 아이콘/색상 설정, 자동 태그 제안

### 📝 Phase 20: 분석 대시보드
- **파일**: [phase-20.md](./phases/phase-20.md)
- **우선순위**: P1
- **주요 내용**: 요약 카드, 인기 게시물 Top 10, 카테고리별 분포

---

## Phase 21-30: 사용자 프론트엔드 - 핵심 UI

### 📝 Phase 21: 프론트엔드 디자인 시스템
- **파일**: [phase-21.md](./phases/phase-21.md)
- **우선순위**: P0
- **주요 내용**: 디자인 토큰, Tailwind CSS/styled-components

### 📝 Phase 22: 공통 컴포넌트 라이브러리
- **파일**: [phase-22.md](./phases/phase-22.md)
- **우선순위**: P0
- **주요 내용**: Button, Card, Modal, Badge, Skeleton

### 📝 Phase 23: 메인 레이아웃
- **파일**: [phase-23.md](./phases/phase-23.md)
- **우선순위**: P0
- **주요 내용**: 헤더, 푸터, 사이드바, 모바일 햄버거 메뉴

### 📝 Phase 24: 홈 피드 - 게시물 카드
- **파일**: [phase-24.md](./phases/phase-24.md)
- **우선순위**: P0
- **주요 내용**: PostCard 컴포넌트, Lazy loading, 반응형 그리드

### 📝 Phase 25: 홈 피드 - 무한 스크롤
- **파일**: [phase-25.md](./phases/phase-25.md)
- **우선순위**: P0
- **주요 내용**: Intersection Observer, 페이지네이션, Pull-to-refresh

### 📝 Phase 26: 게시물 상세 페이지
- **파일**: [phase-26.md](./phases/phase-26.md)
- **우선순위**: P0
- **주요 내용**: 마크다운 렌더링, 이미지 뷰어, 공유 버튼, 관련 게시물

### 📝 Phase 27: 카테고리 페이지
- **파일**: [phase-27.md](./phases/phase-27.md)
- **우선순위**: P1
- **주요 내용**: 카테고리별 게시물, 정렬 옵션

### 📝 Phase 28: 검색 기능
- **파일**: [phase-28.md](./phases/phase-28.md)
- **우선순위**: P1
- **주요 내용**: PostgreSQL Full-Text Search, 검색 UI, 하이라이팅

### 📝 Phase 29: 필터 및 정렬
- **파일**: [phase-29.md](./phases/phase-29.md)
- **우선순위**: P1
- **주요 내용**: 다중 필터, 정렬 드롭다운, URL 쿼리 파라미터

### 📝 Phase 30: 다크모드
- **파일**: [phase-30.md](./phases/phase-30.md)
- **우선순위**: P1
- **주요 내용**: 테마 Context, 토글 버튼, 로컬 스토리지

---

## Phase 31-40: 고급 UX 및 최적화

### 📝 Phase 31: 애니메이션
- **파일**: [phase-31.md](./phases/phase-31.md)
- **우선순위**: P2
- **주요 내용**: Framer Motion, 페이지 전환, 카드 애니메이션

### 📝 Phase 32: 모바일 UX 극대화
- **파일**: [phase-32.md](./phases/phase-32.md)
- **우선순위**: P2
- **주요 내용**: 터치 제스처, 스와이프, 하단 탭 바

### 📝 Phase 33: PWA 기능
- **파일**: [phase-33.md](./phases/phase-33.md)
- **우선순위**: P2
- **주요 내용**: Service Worker, Web App Manifest, 오프라인 지원

### 📝 Phase 34: 성능 최적화 - 프론트엔드
- **파일**: [phase-34.md](./phases/phase-34.md)
- **우선순위**: P2
- **주요 내용**: Code splitting, 이미지 최적화, Lighthouse 95+

### 📝 Phase 35: 성능 최적화 - 백엔드
- **파일**: [phase-35.md](./phases/phase-35.md)
- **우선순위**: P2
- **주요 내용**: Flask-Caching, DB 인덱스, Gzip 압축

### 📝 Phase 36: SEO 최적화
- **파일**: [phase-36.md](./phases/phase-36.md)
- **우선순위**: P1
- **주요 내용**: 메타태그, Sitemap, Schema.org, Open Graph

### 📝 Phase 37: Google AdSense 통합
- **파일**: [phase-37.md](./phases/phase-37.md)
- **우선순위**: P1
- **주요 내용**: AdSense 계정, 광고 유닛, Lazy load 광고

### 📝 Phase 38: 소셜 기능
- **파일**: [phase-38.md](./phases/phase-38.md)
- **우선순위**: P2
- **주요 내용**: 조회수, 공유 카운터, 좋아요

### 📝 Phase 39: 분석 및 모니터링
- **파일**: [phase-39.md](./phases/phase-39.md)
- **우선순위**: P2
- **주요 내용**: Google Analytics 4, 에러 추적, Web Vitals

### 📝 Phase 40: 콘텐츠 추천 시스템
- **파일**: [phase-40.md](./phases/phase-40.md)
- **우선순위**: P2
- **주요 내용**: 관련 게시물, 인기 게시물 위젯

---

## Phase 41-50: 배포 및 운영 (저비용 전략)

### 📝 Phase 41: 로컬 서버 배포 준비
- **파일**: [phase-41.md](./phases/phase-41.md)
- **우선순위**: P0
- **주요 내용**: Docker Compose 프로덕션, Nginx, SSL

### 📝 Phase 42: VPS 선택 및 설정
- **파일**: [phase-42.md](./phases/phase-42.md)
- **우선순위**: P0
- **주요 내용**: Contabo/Oracle Cloud, Ubuntu 설정, 방화벽

### 📝 Phase 43: CI/CD 파이프라인
- **파일**: [phase-43.md](./phases/phase-43.md)
- **우선순위**: P1
- **주요 내용**: GitHub Actions, 자동 배포, 롤백 전략

### 📝 Phase 44: 데이터베이스 운영
- **파일**: [phase-44.md](./phases/phase-44.md)
- **우선순위**: P1
- **주요 내용**: PostgreSQL 프로덕션, 자동 백업, 복구 테스트

### 📝 Phase 45: 이미지 저장소 전략
- **파일**: [phase-45.md](./phases/phase-45.md)
- **우선순위**: P1
- **주요 내용**: 로컬 파일 시스템, Nginx 서빙, 압축 자동화

### 📝 Phase 46: 보안 강화
- **파일**: [phase-46.md](./phases/phase-46.md)
- **우선순위**: P1
- **주요 내용**: Rate limiting, CSRF/XSS 방지, Fail2Ban

### 📝 Phase 47: 로깅 및 모니터링
- **파일**: [phase-47.md](./phases/phase-47.md)
- **우선순위**: P1
- **주요 내용**: 애플리케이션 로그, Uptime 모니터링, 알림

### 📝 Phase 48: AI 모델 최적화
- **파일**: [phase-48.md](./phases/phase-48.md)
- **우선순위**: P1
- **주요 내용**: 모델 양자화, vLLM 최적화, GPU 메모리 모니터링

### 📝 Phase 49: 테스트 및 품질 관리
- **파일**: [phase-49.md](./phases/phase-49.md)
- **우선순위**: P2
- **주요 내용**: Unit Test, E2E Test, 테스트 커버리지 60%+

### 📝 Phase 50: 문서화 및 유지보수
- **파일**: [phase-50.md](./phases/phase-50.md)
- **우선순위**: P2
- **주요 내용**: API 문서 (Swagger), 운영 매뉴얼, AI 프롬프트 라이브러리

---

## 진행 상황 추적

### 완료된 Phase
- ✅ Phase 0: 프로젝트 기획 및 로드맵 (2025-11-15)
- ✅ 상세 가이드 작성: Phase 1, 2, 5

### 현재 진행 중
- 🔄 Phase 1 구현 대기

### 우선순위별 요약

#### P0 (필수 - MVP)
Phase 1, 2, 3, 4, 5, 9, 10, 11, 13, 21, 22, 23, 24, 25, 26, 41, 42

#### P1 (중요)
Phase 6, 7, 8, 12, 14-20, 27-30, 36-37, 43-47

#### P2 (향후 개선)
Phase 31-35, 38-40, 48-50

---

## 사용 팁

### Phase 시작 전
1. 이전 Phase 완료 여부 확인
2. 선행 요구사항 체크
3. 예상 소요 시간 확보

### Phase 진행 중
1. 단계별로 차근차근 진행
2. 완료 체크리스트 활용
3. 문제 발생 시 문제 해결 섹션 참조

### Phase 완료 후
1. 모든 체크리스트 확인
2. `PROGRESS.md`에 기록
3. Git 커밋
4. 다음 Phase로 이동

---

## 관련 문서

- [전체 로드맵](../DEVELOPMENT_ROADMAP.md)
- [진행 상황 추적](../PROGRESS.md)
- [로컬 LLM 설정](../LOCAL_LLM_SETUP.md)
- [빠른 시작 가이드](../QUICK_START_GUIDE.md)

---

**버전**: 1.0
**최종 업데이트**: 2025-11-15
