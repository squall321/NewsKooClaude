#!/usr/bin/env python3
"""모든 Phase 파일을 상세하게 생성하는 스크립트"""
import os

PHASES_DIR = "/home/user/NewsKooClaude/docs/phases"

# Phase별 상세 정보 (Dictionary)
PHASE_DETAILS = {
    3: {
        "title": "Flask 기본 API 구조",
        "difficulty": 3,
        "time": "2-3시간",
        "priority": "P0",
        "goal": "RESTful API 아키텍처를 구축하고, Flask Blueprint를 사용하여 확장 가능한 API 구조를 만듭니다.",
        "key_tasks": [
            "Flask Blueprint 구조 설계",
            "Posts API 엔드포인트 (CRUD)",
            "Categories API 구현",
            "CORS 설정",
            "Error handling middleware",
            "Logging 설정",
            "JWT 데코레이터 구현",
            "Pagination 헬퍼",
            "API 테스트 (pytest)"
        ],
        "code_files": [
            "app/api/__init__.py",
            "app/api/v1/posts.py",
            "app/api/v1/categories.py",
            "app/utils/errors.py",
            "app/utils/decorators.py",
            "app/utils/pagination.py"
        ]
    },
    4: {
        "title": "인증 시스템 (관리자용)",
        "difficulty": 3,
        "time": "2-3시간",
        "priority": "P0",
        "goal": "JWT 토큰 기반 인증 시스템을 구축하여 관리자와 작성자를 위한 보안 인증을 제공합니다.",
        "key_tasks": [
            "JWT 토큰 생성 및 검증",
            "Login API (/api/v1/auth/login)",
            "Token Refresh API",
            "비밀번호 해싱 (bcrypt)",
            "Protected route decorator",
            "User CRUD API",
            "인증 테스트"
        ],
        "code_files": [
            "app/api/v1/auth.py",
            "app/utils/decorators.py (jwt_required)",
            "tests/test_auth.py"
        ]
    },
    # ... Phase 6-50 추가됩니다
}

# 각 Phase 그룹의 일반적인 구조
PHASE_GROUPS = {
    "1-10": "프로젝트 초기 설정 및 기반 구축",
    "11-20": "관리자 대시보드 (작성 중심)",
    "21-30": "사용자 프론트엔드 - 핵심 UI",
    "31-40": "고급 UX 및 최적화",
    "41-50": "배포 및 운영 (저비용 전략)"
}

def get_difficulty_stars(level):
    """난이도를 별로 변환"""
    full = "⭐" * level
    empty = "☆" * (5 - level)
    return full + empty

def generate_phase_content(phase_num, details):
    """Phase 파일 내용 생성"""

    template = f"""# Phase {phase_num:02d}: {details['title']}

**난이도**: {get_difficulty_stars(details['difficulty'])}
**예상 소요 시간**: {details['time']}
**우선순위**: {details['priority']}

## 목표

{details['goal']}

## 선행 요구사항

- Phase {phase_num-1} 완료
- 관련 기술 스택 기본 이해

---

## 주요 구현 내용

### 핵심 작업

{chr(10).join([f"{i+1}. {task}" for i, task in enumerate(details['key_tasks'])])}

---

## 구현 파일

생성/수정할 파일:
{chr(10).join([f"- `{file}`" for file in details['code_files']])}

---

## 구현 단계

### 1단계: 프로젝트 준비

[이 Phase를 시작하기 전에 필요한 준비사항]

### 2단계: 핵심 구현

[주요 코드 구현 내용]

### 3단계: 테스트

[테스트 코드 작성 및 실행]

### 4단계: 통합

[전체 시스템에 통합]

---

## 완료 체크리스트

{chr(10).join([f"- [ ] {task}" for task in details['key_tasks']])}
- [ ] 테스트 통과
- [ ] PROGRESS.md 업데이트
- [ ] Git 커밋

---

## 코드 예시

### 핵심 코드 스니펫

```python
# TODO: 실제 구현 코드는 각 Phase 작업 시 추가
# 이 섹션은 구현 가이드로 사용됩니다
```

---

## 테스트

```python
# 테스트 코드 예시
# pytest로 실행 가능한 테스트
```

---

## 문제 해결

### 자주 발생하는 문제

1. **문제 1**: [설명]
   - **해결**: [방법]

2. **문제 2**: [설명]
   - **해결**: [방법]

---

## 다음 단계

Phase {phase_num} 완료 후:
1. Git 커밋 및 푸시
2. PROGRESS.md 업데이트
3. Phase {phase_num + 1}로 이동

---

**참고 문서**:
- [전체 로드맵](../DEVELOPMENT_ROADMAP.md)
- [Phase Index](../PHASE_INDEX.md)

**완료 기준**:
- 모든 체크리스트 항목 완료
- 테스트 통과
- 실제 작동 확인
"""
    return template

def create_default_phase(phase_num):
    """기본 템플릿 Phase 생성 (상세 정보 없는 경우)"""

    # Phase 번호로 그룹 결정
    if 1 <= phase_num <= 10:
        group = "프로젝트 초기 설정 및 기반 구축"
    elif 11 <= phase_num <= 20:
        group = "관리자 대시보드"
    elif 21 <= phase_num <= 30:
        group = "사용자 프론트엔드"
    elif 31 <= phase_num <= 40:
        group = "고급 UX 및 최적화"
    else:
        group = "배포 및 운영"

    template = f"""# Phase {phase_num:02d}: [구현 대기 중]

**난이도**: ⭐⭐⭐☆☆
**예상 소요 시간**: 2-4시간
**우선순위**: P1
**그룹**: {group}

## 목표

이 Phase의 구체적인 목표는 구현 시작 전에 정의됩니다.

## 구현 내용

이 Phase는 다음을 포함합니다:
- [DEVELOPMENT_ROADMAP.md](../DEVELOPMENT_ROADMAP.md)의 Phase {phase_num} 설명 참조
- 필요한 구현 내용은 작업 시작 시 상세히 작성됩니다

## 완료 체크리스트

- [ ] Phase {phase_num} 요구사항 분석
- [ ] 핵심 기능 구현
- [ ] 테스트 작성 및 통과
- [ ] 문서화
- [ ] PROGRESS.md 업데이트

## 다음 단계

Phase {phase_num} 완료 후 Phase {phase_num + 1 if phase_num < 50 else "완료"}로 이동

---

**📝 상세 가이드 필요 시**:
이 Phase의 상세 구현 가이드가 필요하면 요청해주세요.
상세 가이드에는 다음이 포함됩니다:
- 단계별 구현 방법
- 코드 예제
- 테스트 방법
- 문제 해결 가이드

**참고**:
- [전체 로드맵](../DEVELOPMENT_ROADMAP.md) - Phase {phase_num} 섹션
- [Phase Index](../PHASE_INDEX.md)
"""
    return template

def main():
    """메인 함수"""
    print("=" * 60)
    print("Phase 파일 생성 스크립트")
    print("=" * 60)

    created_count = 0
    updated_count = 0

    # Phase 3-50 생성 (1, 2, 5는 이미 상세함)
    for i in range(3, 51):
        if i == 5:  # Phase 5는 별도로 상세 작성 필요
            continue

        filename = f"phase-{i:02d}.md"
        filepath = os.path.join(PHASES_DIR, filename)

        # 상세 정보가 있으면 사용, 없으면 기본 템플릿
        if i in PHASE_DETAILS:
            content = generate_phase_content(i, PHASE_DETAILS[i])
            status = "상세"
        else:
            content = create_default_phase(i)
            status = "기본"

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        if os.path.exists(filepath):
            updated_count += 1
        else:
            created_count += 1

        print(f"✓ Phase {i:02d}: {status} 템플릿 생성")

    print("\n" + "=" * 60)
    print(f"✅ 완료!")
    print(f"   생성: {created_count}개")
    print(f"   업데이트: {updated_count}개")
    print("=" * 60)

    print("\n📝 상세 작성 완료:")
    print("   - Phase 01, 02: 이미 작성됨")
    print("   - Phase 03, 04: 스크립트로 생성")
    print("   - Phase 05: 별도 복원 필요")
    print("   - Phase 06-50: 기본 템플릿")

    print("\n💡 다음 단계:")
    print("   1. Phase 5 복원 (로컬 LLM 환경)")
    print("   2. 중요 Phase (6-10) 상세 작성")
    print("   3. 각 Phase 구현 시작")

if __name__ == "__main__":
    main()
