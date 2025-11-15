#!/usr/bin/env python3
"""
포괄적인 Phase 파일 생성기
Phase 1-50 모두를 최대한 상세하게 생성합니다
"""
import os

PHASES_DIR = "/home/user/NewsKooClaude/docs/phases"

# 모든 Phase의 상세 정보
ALL_PHASES = {
    1: {
        "title": "프로젝트 구조 및 개발 환경 설정",
        "difficulty": 2, "time": "2-3시간", "priority": "P0",
        "goal": "프론트엔드(React + TypeScript + Vite)와 백엔드(Flask) 프로젝트의 기본 골격을 생성하고 개발 도구를 설정합니다.",
        "key_tasks": ["Vite React TypeScript 프로젝트 생성", "Flask 프로젝트 구조", "ESLint/Prettier 설정", "환경변수 관리", "디렉토리 구조 설계"],
        "files": ["frontend/", "backend/", ".gitignore", ".env.example"]
    },
    2: {
        "title": "데이터베이스 설계 및 모델 정의",
        "difficulty": 3, "time": "3-4시간", "priority": "P0",
        "goal": "재창작 철학을 반영한 데이터베이스 스키마를 설계하고 SQLAlchemy 모델을 정의합니다.",
        "key_tasks": ["ERD 설계", "User/Post/Category/Tag 모델", "Inspiration/Draft/WritingStyle 모델", "Flask-Migrate 설정", "시드 데이터"],
        "files": ["app/models/*.py", "migrations/", "scripts/seed_data.py"]
    },
    3: {
        "title": "Flask 기본 API 구조",
        "difficulty": 3, "time": "2-3시간", "priority": "P0",
        "goal": "RESTful API 아키텍처를 구축하고 Flask Blueprint로 확장 가능한 구조를 만듭니다.",
        "key_tasks": ["Blueprint 구조", "Posts/Categories API", "CORS 설정", "Error handling", "Logging", "JWT 데코레이터"],
        "files": ["app/api/v1/*.py", "app/utils/errors.py", "app/utils/decorators.py"]
    },
    4: {
        "title": "인증 시스템 (관리자용)",
        "difficulty": 3, "time": "2-3시간", "priority": "P0",
        "goal": "JWT 기반 인증으로 관리자와 작성자를 위한 보안 시스템을 구축합니다.",
        "key_tasks": ["JWT 토큰 생성/검증", "Login API", "Token Refresh", "비밀번호 해싱", "Protected routes"],
        "files": ["app/api/v1/auth.py", "tests/test_auth.py"]
    },
    5: {
        "title": "로컬 LLM 환경 구축 ⭐",
        "difficulty": 5, "time": "4-6시간", "priority": "P0",
        "goal": "RTX 5070 TI로 EEVE-Korean-10.8B를 실행하여 API 비용 제로를 달성합니다.",
        "key_tasks": ["CUDA 12.1 설치", "PyTorch CUDA 설정", "EEVE 모델 다운로드", "INT8 양자화", "LLMModelLoader 구현", "추론 테스트"],
        "files": ["app/llm/model_loader.py", "scripts/download_model.py", "scripts/quantize_model.py"]
    },
    6: {
        "title": "AI 재구성 엔진 - 프롬프트 설계",
        "difficulty": 4, "time": "3-4시간", "priority": "P1",
        "goal": "효과적인 유머 재창작을 위한 프롬프트 시스템을 구축합니다.",
        "key_tasks": ["프롬프트 템플릿", "Few-shot examples DB", "유사도 체크", "스타일별 프롬프트", "품질 평가"],
        "files": ["app/llm/prompts.py", "app/services/ai_rewriter.py"]
    },
    7: {
        "title": "Reddit 영감 수집 시스템",
        "difficulty": 3, "time": "2-3시간", "priority": "P1",
        "goal": "PRAW로 Reddit 유머를 메타데이터만 수집하여 저작권을 준수합니다.",
        "key_tasks": ["PRAW 설정", "Subreddit 모니터링", "메타데이터 수집", "인기도 필터링", "중복 체크"],
        "files": ["app/services/crawler.py", "scripts/test_reddit_api.py"]
    },
    8: {
        "title": "크롤링 스케줄러",
        "difficulty": 3, "time": "2시간", "priority": "P1",
        "goal": "APScheduler로 자동 주기적 크롤링을 설정합니다.",
        "key_tasks": ["APScheduler 통합", "일일 1-2회 크롤링", "실패 재시도", "크롤링 상태 API"],
        "files": ["app/services/scheduler.py", "app/api/v1/crawler_status.py"]
    },
    9: {
        "title": "수동 작성 우선 시스템",
        "difficulty": 3, "time": "3-4시간", "priority": "P0",
        "goal": "작성자가 직접 글을 쉽게 쓸 수 있는 Draft 시스템을 만듭니다.",
        "key_tasks": ["Draft CRUD API", "마크다운 에디터 백엔드", "이미지 업로드", "자동 저장", "발행/예약"],
        "files": ["app/api/v1/drafts.py", "app/services/image_processor.py"]
    },
    10: {
        "title": "AI 보조 작성 인터페이스",
        "difficulty": 4, "time": "3-4시간", "priority": "P0",
        "goal": "AI가 초안을 제안하면 사람이 다듬는 협업 시스템을 구축합니다.",
        "key_tasks": ["AI 재구성 API", "여러 버전 생성", "유사도 경고", "문단 개선", "제목 생성"],
        "files": ["app/api/v1/ai_assistant.py", "app/services/ai_rewriter.py"]
    },
    13: {
        "title": "글 작성 에디터",
        "difficulty": 3, "time": "3-4시간", "priority": "P0",
        "goal": "직관적인 마크다운 에디터를 React로 구현합니다.",
        "key_tasks": ["마크다운 에디터 통합", "실시간 미리보기", "이미지 드래그앤드롭", "자동 저장", "발행 버튼"],
        "files": ["frontend/src/components/admin/MarkdownEditor.tsx", "frontend/src/pages/admin/CreatePost.tsx"]
    },
    21: {
        "title": "프론트엔드 디자인 시스템",
        "difficulty": 3, "time": "3-4시간", "priority": "P0",
        "goal": "모바일 우선의 일관된 UI/UX 디자인 시스템을 구축합니다.",
        "key_tasks": ["디자인 토큰", "색상 팔레트", "타이포그래피", "간격 시스템", "Tailwind/styled-components"],
        "files": ["frontend/src/styles/theme.ts", "frontend/src/styles/global.css", "tailwind.config.js"]
    },
    22: {
        "title": "공통 컴포넌트 라이브러리",
        "difficulty": 3, "time": "3-4시간", "priority": "P0",
        "goal": "재사용 가능한 UI 컴포넌트를 만듭니다.",
        "key_tasks": ["Button", "Card", "Modal", "Badge", "Skeleton", "Toast", "Icon 시스템"],
        "files": ["frontend/src/components/common/Button.tsx", "frontend/src/components/common/Card.tsx"]
    },
    23: {
        "title": "메인 레이아웃",
        "difficulty": 2, "time": "2-3시간", "priority": "P0",
        "goal": "깔끔한 헤더/푸터/사이드바 레이아웃을 만듭니다.",
        "key_tasks": ["헤더", "푸터", "모바일 햄버거 메뉴", "카테고리 네비게이션", "다크모드 토글"],
        "files": ["frontend/src/components/layout/Header.tsx", "frontend/src/components/layout/Footer.tsx"]
    },
    24: {
        "title": "홈 피드 - 게시물 카드",
        "difficulty": 3, "time": "2-3시간", "priority": "P0",
        "goal": "클릭하고 싶게 만드는 매력적인 게시물 카드를 만듭니다.",
        "key_tasks": ["PostCard 컴포넌트", "썸네일/제목/요약", "카테고리 배지", "Lazy loading", "반응형 그리드"],
        "files": ["frontend/src/components/post/PostCard.tsx", "frontend/src/pages/Home.tsx"]
    },
    25: {
        "title": "홈 피드 - 무한 스크롤",
        "difficulty": 3, "time": "2-3시간", "priority": "P0",
        "goal": "끊김 없는 콘텐츠 탐색을 위한 무한 스크롤을 구현합니다.",
        "key_tasks": ["Intersection Observer", "페이지네이션 연동", "Loading skeleton", "Pull-to-refresh"],
        "files": ["frontend/src/hooks/useInfiniteScroll.ts", "frontend/src/pages/Home.tsx"]
    },
    26: {
        "title": "게시물 상세 페이지",
        "difficulty": 3, "time": "2-3시간", "priority": "P0",
        "goal": "최고의 읽기 경험을 제공하는 상세 페이지를 만듭니다.",
        "key_tasks": ["마크다운 렌더링", "이미지 뷰어", "공유 버튼", "관련 게시물", "조회수 카운터"],
        "files": ["frontend/src/pages/PostDetail.tsx", "frontend/src/components/post/MarkdownRenderer.tsx"]
    },
    41: {
        "title": "로컬 서버 배포 준비",
        "difficulty": 4, "time": "3-4시간", "priority": "P0",
        "goal": "Docker Compose와 Nginx로 프로덕션 환경을 구축합니다.",
        "key_tasks": ["Docker Compose 프로덕션", "Nginx 설정", "SSL (Let's Encrypt)", "환경 변수 관리"],
        "files": ["docker-compose.prod.yml", "nginx.conf", "Dockerfile"]
    },
    42: {
        "title": "VPS 선택 및 설정",
        "difficulty": 4, "time": "3-4시간", "priority": "P0",
        "goal": "저렴한 VPS를 선택하고 Ubuntu를 설정합니다.",
        "key_tasks": ["VPS 선택 (Contabo/Oracle)", "Ubuntu 22.04 설치", "Docker 설치", "방화벽 설정", "도메인 연결"],
        "files": ["docs/DEPLOYMENT_GUIDE.md"]
    }
}

def get_difficulty_stars(level):
    return "⭐" * level + "☆" * (5 - level)

def create_detailed_phase(num, info):
    """상세한 Phase 파일 생성"""
    return f"""# Phase {num:02d}: {info['title']}

**난이도**: {get_difficulty_stars(info['difficulty'])}
**예상 소요 시간**: {info['time']}
**우선순위**: {info['priority']}

## 목표

{info['goal']}

## 선행 요구사항

- Phase {num-1 if num > 1 else '0 (계획)'} 완료
- 관련 기술 스택 기본 이해

---

## 주요 구현 내용

### 핵심 작업

{chr(10).join([f"{i+1}. **{task}**" for i, task in enumerate(info['key_tasks'])])}

---

## 생성/수정할 파일

{chr(10).join([f"- `{file}`" for file in info['files']])}

---

## 구현 단계

### 1단계: 환경 준비

이 Phase를 시작하기 전에 필요한 도구와 라이브러리를 설치합니다.

**확인 사항**:
- 이전 Phase 완료 확인
- 필요한 패키지 설치
- 개발 서버 실행 상태 확인

### 2단계: 핵심 구현

{chr(10).join([f"**{i+1}. {task}**" for i, task in enumerate(info['key_tasks'])])}

각 작업은 순차적으로 진행하며, 테스트를 거쳐 검증합니다.

### 3단계: 테스트

```python
# 테스트 코드 작성 예시
# pytest tests/test_phase_{num:02d}.py -v
```

**테스트 항목**:
- 단위 테스트 (Unit Test)
- 통합 테스트 (Integration Test)
- 수동 테스트 (Manual Test)

### 4단계: 통합 및 검증

- 전체 시스템과 통합
- 기존 기능에 영향 없는지 확인
- 성능 테스트

---

## 완료 체크리스트

### 구현
{chr(10).join([f"- [ ] {task}" for task in info['key_tasks']])}

### 품질 보증
- [ ] 코드 리뷰 (자체)
- [ ] 테스트 작성 및 통과
- [ ] 에러 핸들링 확인
- [ ] 로깅 적절히 추가

### 문서화
- [ ] 코드 주석 작성
- [ ] PROGRESS.md 업데이트
- [ ] Git 커밋 메시지 작성

---

## 코드 예제

### 핵심 구현

```python
# TODO: Phase {num} 구현 시 실제 코드 추가
# 이 섹션은 구현 가이드로 활용됩니다

# 예시 코드 구조는 다음과 같습니다:
# 1. Import 문
# 2. 설정
# 3. 핵심 로직
# 4. Export
```

---

## 테스트

### 단위 테스트

```python
# tests/test_phase_{num:02d}.py
import pytest

def test_phase_{num}_functionality():
    '''Phase {num} 기능 테스트'''
    # TODO: 테스트 구현
    pass
```

### 실행

```bash
pytest tests/test_phase_{num:02d}.py -v
```

---

## 문제 해결

### 자주 발생하는 문제

**문제 1**: [일반적인 문제]
- **증상**: [현상 설명]
- **원인**: [원인 분석]
- **해결**: [해결 방법]

**문제 2**: [성능 관련]
- **증상**: [느린 속도 등]
- **원인**: [병목 지점]
- **해결**: [최적화 방법]

---

## 다음 단계

Phase {num} 완료 후:

1. **코드 커밋**
   ```bash
   git add .
   git commit -m "Phase {num}: {info['title']}"
   git push origin your-branch
   ```

2. **PROGRESS.md 업데이트**
   - 완료 날짜 기록
   - 주요 구현 내용 요약
   - 배운 점 기록

3. **Phase {num + 1 if num < 50 else '완료'}로 이동**

---

## 참고 자료

- [전체 로드맵](../DEVELOPMENT_ROADMAP.md#phase-{num})
- [Phase Index](../PHASE_INDEX.md)
- [관련 기술 문서]

---

**완료 기준**:
✅ 모든 체크리스트 항목 완료
✅ 테스트 통과 (100%)
✅ 실제 작동 확인
✅ 문서화 완료
"""

def create_basic_phase(num):
    """기본 템플릿 Phase"""
    group = ["", "프로젝트 기반", "관리자 대시보드", "사용자 프론트엔드", "고급 기능", "배포 및 운영"][num // 10]

    return f"""# Phase {num:02d}: [상세 작성 대기]

**난이도**: ⭐⭐⭐☆☆
**예상 소요 시간**: 2-4시간
**우선순위**: P1
**분류**: {group}

## 목표

이 Phase의 구체적인 목표는 [DEVELOPMENT_ROADMAP.md](../DEVELOPMENT_ROADMAP.md)의 Phase {num} 섹션을 참조하세요.

## 구현 가이드

**이 Phase는 다음을 포함합니다**:

1. [DEVELOPMENT_ROADMAP.md](../DEVELOPMENT_ROADMAP.md#phase-{num}) 참조
2. 구현 시작 시 상세 내용 작성 예정

## 완료 체크리스트

- [ ] Phase {num} 요구사항 분석
- [ ] 핵심 기능 구현
- [ ] 테스트 작성 및 통과
- [ ] 문서화
- [ ] PROGRESS.md 업데이트
- [ ] Git 커밋

## 다음 단계

Phase {num} 완료 후 Phase {num + 1 if num < 50 else '완료'}로 이동

---

**💡 상세 가이드 요청**

이 Phase의 상세 구현 가이드가 필요하시면:
1. Phase {num}의 핵심 내용 확인
2. 필요한 부분 구체화
3. 상세 가이드 요청

**포함될 내용**:
- 단계별 구현 방법
- 코드 예제 및 설명
- 테스트 전략
- 문제 해결 가이드
- Best Practices

**참고 문서**:
- [전체 로드맵](../DEVELOPMENT_ROADMAP.md)
- [Phase Index](../PHASE_INDEX.md)
"""

def main():
    print("=" * 70)
    print("📚 포괄적인 Phase 파일 생성기")
    print("=" * 70)

    detailed = 0
    basic = 0

    for i in range(1, 51):
        filename = f"phase-{i:02d}.md"
        filepath = os.path.join(PHASES_DIR, filename)

        if i in ALL_PHASES:
            content = create_detailed_phase(i, ALL_PHASES[i])
            status = "✨ 상세"
            detailed += 1
        else:
            content = create_basic_phase(i)
            status = "📝 기본"
            basic += 1

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"{status} | Phase {i:02d}: {ALL_PHASES.get(i, {}).get('title', '작성 대기')}")

    print("\n" + "=" * 70)
    print(f"✅ 완료!")
    print(f"   상세 작성: {detailed}개 Phase")
    print(f"   기본 템플릿: {basic}개 Phase")
    print(f"   총 Phase: 50개")
    print("=" * 70)

    print("\n📊 상세 작성된 Phase:")
    for num in sorted(ALL_PHASES.keys()):
        print(f"   Phase {num:02d}: {ALL_PHASES[num]['title']}")

    print("\n💡 다음 작업:")
    print("   1. 각 Phase 시작 시 상세 내용 확장")
    print("   2. 코드 예제 추가")
    print("   3. 실제 구현 진행")

if __name__ == "__main__":
    main()
