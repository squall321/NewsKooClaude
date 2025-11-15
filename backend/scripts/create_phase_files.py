#!/usr/bin/env python3
"""Phase 3-50 템플릿 파일 생성"""
import os

PHASES_DIR = "/home/user/NewsKooClaude/docs/phases"

template = """# Phase {num}: [구현 예정]

**난이도**: ⭐⭐⭐☆☆
**예상 소요 시간**: X시간
**우선순위**: PX

## 목표

[이 Phase의 목표를 기술합니다]

## 주요 구현 내용

[구현할 내용을 기술합니다]

## 완료 체크리스트

- [ ] 작업 항목 1
- [ ] 작업 항목 2
- [ ] 작업 항목 3

## 다음 단계

Phase {num} 완료 후 Phase {next}로 이동

---

**참고**: 이 Phase의 상세 가이드는 필요 시 작성됩니다.
상세 가이드가 필요하면 요청해주세요.
"""

# Phase 3-50 생성 (1, 2, 5는 이미 상세하게 작성됨)
for i in range(3, 51):
    if i == 5:  # Phase 5는 이미 작성됨
        continue

    filename = f"phase-{i:02d}.md"
    filepath = os.path.join(PHASES_DIR, filename)

    content = template.format(num=i, next=i+1 if i < 50 else "완료")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✓ Created {filename}")

print(f"\n✅ Total files created: 47")
print(f"✅ Already detailed: Phase 01, 02, 05")
print(f"✅ Total phases: 50")
