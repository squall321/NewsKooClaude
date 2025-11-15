# Components

재사용 가능한 React 컴포넌트들을 저장합니다.

## 디렉토리 구조

```
components/
├── common/          # 공통 컴포넌트 (Button, Input, Card 등)
├── layout/          # 레이아웃 컴포넌트 (Header, Footer, Sidebar 등)
├── post/            # 게시물 관련 컴포넌트
├── admin/           # 관리자 전용 컴포넌트
└── ui/              # 기본 UI 컴포넌트
```

## 컴포넌트 작성 가이드

1. 각 컴포넌트는 별도의 폴더에 위치
2. `ComponentName.tsx` - 메인 컴포넌트
3. `ComponentName.test.tsx` - 테스트 파일
4. `ComponentName.module.css` - 스타일 (필요시)
5. `index.ts` - export 전용 파일
