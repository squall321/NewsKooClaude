#!/usr/bin/env python3
"""
콘텐츠 생성 서비스 테스트 스크립트

Phase 6에서 구현한 AI 콘텐츠 생성 및 유사도 체크를 테스트합니다.
"""
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.llm.prompts import PromptTemplate, HumorStyle
from app.services.similarity_checker import SimilarityChecker


def test_prompt_templates():
    """프롬프트 템플릿 테스트"""
    print("=" * 80)
    print("TEST 1: Prompt Templates")
    print("=" * 80)
    print()

    # 기본 시스템 프롬프트
    print("--- Base System Prompt ---")
    base_prompt = PromptTemplate.get_system_prompt()
    print(base_prompt[:300] + "...")
    print()

    # 스타일별 프롬프트
    print("--- Casual Style System Prompt ---")
    casual_prompt = PromptTemplate.get_system_prompt(HumorStyle.CASUAL)
    print(casual_prompt[:300] + "...")
    print()

    # Few-shot 예제
    print("--- Few-shot Examples (Casual) ---")
    examples = PromptTemplate.get_few_shot_examples(HumorStyle.CASUAL, count=1)
    if examples:
        ex = examples[0]
        print(f"Original: {ex['original']}")
        print(f"Recreated: {ex['recreated'][:200]}...")
    print()

    # 전체 프롬프트 구성
    print("--- Full Prompt Construction ---")
    system, user = PromptTemplate.build_full_prompt(
        original_concept="Someone accidentally sends a message to their boss instead of their friend",
        style=HumorStyle.CASUAL,
        use_few_shot=True,
        few_shot_count=1
    )
    print(f"System Prompt Length: {len(system)} chars")
    print(f"User Prompt Length: {len(user)} chars")
    print(f"User Prompt Preview: {user[:300]}...")
    print()


def test_similarity_checker():
    """유사도 체크 테스트"""
    print("=" * 80)
    print("TEST 2: Similarity Checker")
    print("=" * 80)
    print()

    checker = SimilarityChecker()

    # 테스트 케이스 1: 높은 유사도 (Fair Use 위반)
    print("--- Test Case 1: High Similarity (Fair Use Violation) ---")
    original1 = "회의 중에 카메라가 꺼져있는 줄 알고 하품을 했는데 사실 켜져있었다"
    generated1 = "미팅 중에 카메라가 off인 줄 알고 하품했는데 실제로는 on이었다"

    result1 = checker.check_similarity(original1, generated1)
    print(f"Original: {original1}")
    print(f"Generated: {generated1}")
    print(f"\n전체 유사도: {result1.overall_similarity:.2%}")
    print(f"구조적 유사도: {result1.structural_similarity:.2%}")
    print(f"어휘적 유사도: {result1.lexical_similarity:.2%}")
    print(f"Fair Use 준수: {'✅ Yes' if result1.is_fair_use_compliant else '❌ No'}")
    print()

    # 리포트
    print(checker.get_fair_use_report(result1))
    print("\n")

    # 테스트 케이스 2: 낮은 유사도 (Fair Use 준수)
    print("--- Test Case 2: Low Similarity (Fair Use Compliant) ---")
    original2 = "Someone accidentally sends embarrassing message to boss"
    generated2 = """**제목**: 단체톡방의 비극

**내용**:
새벽 2시, 친구들이랑 게임하다가 단체톡방에 실수로 메시지를 보냈다.

"야 오늘 팀장님 머리 진짜 웃기지 않았어? ㅋㅋㅋㅋ"

...잘못 보낸 톡방은 회사 TF 단체톡방.

3초 뒤, 팀장님이 답장했다.

"민수야, 내일 오전 9시에 내 자리로 와보렴."

친구톡에서 위로가 쏟아졌다.

"ㅋㅋㅋㅋㅋㅋ 민수야 안녕"
"유서 써라"
"헤드가 아니라 헤드헌팅 당할 듯"

다음날 사표 쓰고 회사 갔다."""

    result2 = checker.check_similarity(original2, generated2)
    print(f"Original: {original2}")
    print(f"Generated: {generated2[:100]}...")
    print(f"\n전체 유사도: {result2.overall_similarity:.2%}")
    print(f"구조적 유사도: {result2.structural_similarity:.2%}")
    print(f"어휘적 유사도: {result2.lexical_similarity:.2%}")
    print(f"Fair Use 준수: {'✅ Yes' if result2.is_fair_use_compliant else '❌ No'}")
    print()

    # 리포트
    print(checker.get_fair_use_report(result2))
    print("\n")

    # 테스트 케이스 3: 배치 체크
    print("--- Test Case 3: Batch Check ---")
    originals = [original1, original2]
    generateds = [generated1, generated2]

    batch_results = checker.batch_check(originals, generateds)
    for i, result in enumerate(batch_results, 1):
        print(f"Pair {i}: {result.overall_similarity:.2%} - "
              f"{'✅ Fair Use' if result.is_fair_use_compliant else '❌ Violation'}")
    print()


def test_humor_styles():
    """다양한 유머 스타일 테스트"""
    print("=" * 80)
    print("TEST 3: Humor Styles")
    print("=" * 80)
    print()

    styles = [
        HumorStyle.CASUAL,
        HumorStyle.ABSURD,
        HumorStyle.WORDPLAY,
        HumorStyle.SITUATIONAL,
        HumorStyle.SARCASM,
        HumorStyle.CUTE,
        HumorStyle.DARK
    ]

    original_concept = "Someone tries to skip a queue and gets called out"

    for style in styles:
        print(f"--- Style: {style.value.upper()} ---")
        system, user = PromptTemplate.build_full_prompt(
            original_concept=original_concept,
            style=style,
            use_few_shot=False  # few-shot 없이 스타일만 확인
        )

        # 스타일별 프롬프트 특징 출력
        style_prompt = PromptTemplate.STYLE_SYSTEM_PROMPTS.get(style, "")
        print(style_prompt[:150] + "...")
        print()


def test_edge_cases():
    """엣지 케이스 테스트"""
    print("=" * 80)
    print("TEST 4: Edge Cases")
    print("=" * 80)
    print()

    checker = SimilarityChecker()

    # 빈 문자열
    print("--- Empty Strings ---")
    result = checker.check_similarity("", "")
    print(f"Similarity: {result.overall_similarity:.2%}")
    print()

    # 매우 짧은 텍스트
    print("--- Very Short Text ---")
    result = checker.check_similarity("안녕", "하이")
    print(f"Similarity: {result.overall_similarity:.2%}")
    print()

    # 동일한 텍스트
    print("--- Identical Text ---")
    text = "이것은 테스트 텍스트입니다."
    result = checker.check_similarity(text, text)
    print(f"Similarity: {result.overall_similarity:.2%}")
    print(f"Should be high: {'✓' if result.overall_similarity > 0.9 else '✗'}")
    print()


def main():
    """메인 실행 함수"""
    print("\n")
    print("=" * 80)
    print("PHASE 6: AI Content Generation & Similarity Checker Test")
    print("=" * 80)
    print("\n")

    try:
        # 1. 프롬프트 템플릿 테스트
        test_prompt_templates()
        input("Press Enter to continue to next test...")
        print("\n")

        # 2. 유사도 체크 테스트
        test_similarity_checker()
        input("Press Enter to continue to next test...")
        print("\n")

        # 3. 유머 스타일 테스트
        test_humor_styles()
        input("Press Enter to continue to next test...")
        print("\n")

        # 4. 엣지 케이스 테스트
        test_edge_cases()

        print("\n")
        print("=" * 80)
        print("All tests completed successfully! ✅")
        print("=" * 80)
        print("\n")
        print("Note: LLM inference tests require model to be loaded.")
        print("Use test_llm_inference.py for full LLM testing.")

    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
