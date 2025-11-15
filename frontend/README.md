# NewsKoo Frontend

React + TypeScript + Vite 기반 유머 콘텐츠 플랫폼 프론트엔드

## 기술 스택

- **Framework**: React 18
- **Language**: TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Routing**: React Router v6
- **State Management**: @tanstack/react-query
- **HTTP Client**: Axios
- **Linting**: ESLint + Prettier

## 디렉토리 구조

```
frontend/
├── src/
│   ├── components/          # 재사용 가능한 컴포넌트
│   │   ├── common/         # 공통 컴포넌트
│   │   ├── layout/         # 레이아웃 컴포넌트
│   │   ├── post/           # 게시물 관련 컴포넌트
│   │   ├── admin/          # 관리자 컴포넌트
│   │   └── ui/             # 기본 UI 컴포넌트
│   ├── pages/              # 페이지 컴포넌트
│   ├── hooks/              # Custom React Hooks
│   ├── services/           # API 서비스
│   ├── types/              # TypeScript 타입 정의
│   ├── contexts/           # React Context
│   ├── utils/              # 유틸리티 함수
│   ├── styles/             # 전역 스타일
│   ├── App.tsx             # 메인 앱 컴포넌트
│   ├── main.tsx            # 엔트리 포인트
│   └── index.css           # Tailwind 설정
├── public/                 # 정적 파일
├── index.html              # HTML 템플릿
├── vite.config.ts          # Vite 설정
├── tsconfig.json           # TypeScript 설정
├── tailwind.config.js      # Tailwind 설정
├── eslint.config.js        # ESLint 설정
└── .prettierrc             # Prettier 설정
```

## 설치 및 실행

### 1. 의존성 설치

```bash
cd frontend
npm install
```

### 2. 환경 변수 설정

`.env.example`을 복사하여 `.env` 파일 생성

```bash
cp .env.example .env
```

### 3. 개발 서버 실행

```bash
npm run dev
```

서버가 `http://localhost:5173`에서 실행됩니다.

## 스크립트

```bash
# 개발 서버 실행
npm run dev

# 프로덕션 빌드
npm run build

# 빌드 결과 미리보기
npm run preview

# 린트 검사
npm run lint
```

## 주요 패키지

### UI/스타일링
- `react` - UI 라이브러리
- `tailwindcss` - 유틸리티 CSS 프레임워크

### 라우팅 & 상태 관리
- `react-router-dom` - 클라이언트 사이드 라우팅
- `@tanstack/react-query` - 서버 상태 관리

### API 통신
- `axios` - HTTP 클라이언트

### 개발 도구
- `typescript` - 타입 안정성
- `eslint` - 코드 품질
- `prettier` - 코드 포맷팅

## 참고 문서

- [React 공식 문서](https://react.dev/)
- [Vite 공식 문서](https://vitejs.dev/)
- [Tailwind CSS 문서](https://tailwindcss.com/)
- [React Router 문서](https://reactrouter.com/)
- [개발 로드맵](../DEVELOPMENT_ROADMAP.md)
