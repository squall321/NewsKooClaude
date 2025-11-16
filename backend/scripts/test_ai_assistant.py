#!/usr/bin/env python3
"""
AI Assistant 테스트 스크립트

AI 보조 작성 기능을 테스트합니다:
- 여러 버전 생성
- 문단 개선
- 제목 생성
- 유사도 체크
- 피드백 기반 재작성
"""
import os
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import create_app, db
from app.models import User, Category, Inspiration, Source
from app.services.ai_rewriter import get_ai_rewriter
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()


def setup_test_data(app):
    """테스트 데이터 생성"""
    print("=== Setting up test data ===\n")

    with app.app_context():
        # 기존 테스트 데이터 삭제
        User.query.filter_by(username='ai_test_user').delete()
        Source.query.filter_by(title='Test Source for AI').delete()

        # 사용자 생성
        user = User.create(
            username='ai_test_user',
            email='ai_test@example.com',
            password='test1234',
            role='editor'
        )
        user_id = user.id

        # 소스 및 Inspiration 생성
        source = Source.create(
            platform='reddit',
            source_id='test_ai_123',
            url='https://reddit.com/r/funny/test',
            title='Test Source for AI',
            author='test_author',
            upvotes=1000,
            comments=100
        )

        inspiration = Inspiration.create(
            source_id=source.id,
            concept='고양이가 키보드 위에서 자다가 실수로 상사에게 이메일을 보냈습니다. 이메일 내용은 "aaaaaasssssdddd"였습니다.',
            similarity_score=0.65
        )

        db.session.commit()

        print(f"✓ Test user created: {user.username} (ID: {user_id})")
        print(f"✓ Test source created: {source.title} (ID: {source.id})")
        print(f"✓ Test inspiration created: {inspiration.concept[:50]}... (ID: {inspiration.id})")
        print()

        return user_id, inspiration.id


def test_generate_versions(app):
    """여러 버전 생성 테스트"""
    print("=" * 80)
    print("TEST 1: Generate Multiple Versions")
    print("=" * 80)
    print()

    with app.app_context():
        ai_rewriter = get_ai_rewriter()

        concept = "고양이가 키보드 위에서 자다가 실수로 상사에게 이메일을 보냈습니다."

        print(f"Original concept: {concept}")
        print()
        print("Generating 3 versions (sarcastic, wholesome, dark)...")
        print()

        versions = ai_rewriter.generate_multiple_versions(
            original_concept=concept,
            styles=['sarcastic', 'wholesome', 'dark'],
            count=3
        )

        for i, version in enumerate(versions, 1):
            print(f"Version {i} ({version.style}):")
            print(f"  Content: {version.content[:200]}...")
            print(f"  Similarity: {version.similarity:.1%}")
            print(f"  Fair Use: {'✓' if version.is_fair_use else '✗'}")
            print(f"  Tokens: {version.metadata.get('completion_tokens', 0)}")
            print()

        print(f"✓ Generated {len(versions)} versions successfully")
        print()


def test_improve_paragraph(app):
    """문단 개선 테스트"""
    print("=" * 80)
    print("TEST 2: Improve Paragraph")
    print("=" * 80)
    print()

    with app.app_context():
        ai_rewriter = get_ai_rewriter()

        paragraph = "고양이가 키보드를 밟았다. 그래서 이메일이 보내졌다."

        print(f"Original paragraph: {paragraph}")
        print()
        print("Improving with goal: '더 재미있고 구체적으로'...")
        print()

        result = ai_rewriter.improve_paragraph(
            paragraph=paragraph,
            improvement_goal="더 재미있고 구체적으로"
        )

        print(f"Improved paragraph:")
        print(f"  {result['improved']}")
        print()
        print(f"Goal: {result['goal']}")
        print(f"Original length: {result['metadata']['original_length']} chars")
        print(f"Improved length: {result['metadata']['improved_length']} chars")
        print(f"Length change: {result['metadata']['length_change']:+d} chars")
        print()

        print("✓ Paragraph improved successfully")
        print()


def test_generate_titles(app):
    """제목 생성 테스트"""
    print("=" * 80)
    print("TEST 3: Generate Titles")
    print("=" * 80)
    print()

    with app.app_context():
        ai_rewriter = get_ai_rewriter()

        content = """
        우리 집 고양이 나비는 평소 키보드 위에서 자는 것을 좋아합니다.
        어제 저녁, 나비가 키보드 위에서 자다가 실수로 발을 여러 번 밟았습니다.
        그 결과, 상사에게 "aaaaaasssssdddd"라는 내용의 이메일이 전송되었습니다.
        다음 날 아침, 상사로부터 "무슨 암호인가요?"라는 답장을 받았습니다.
        """

        print(f"Content preview: {content[:100].strip()}...")
        print()
        print("Generating 3 catchy titles...")
        print()

        titles = ai_rewriter.generate_title(
            content=content,
            style='catchy',
            count=3
        )

        for i, title in enumerate(titles, 1):
            print(f"{i}. {title}")

        print()
        print(f"✓ Generated {len(titles)} titles successfully")
        print()


def test_check_similarity(app):
    """유사도 체크 테스트"""
    print("=" * 80)
    print("TEST 4: Check Similarity (Fair Use)")
    print("=" * 80)
    print()

    with app.app_context():
        ai_rewriter = get_ai_rewriter()

        original = "고양이가 키보드 위에서 자다가 이메일을 보냈다."
        generated1 = "고양이가 키보드 위에서 자다가 이메일을 보냈다."  # 동일
        generated2 = "우리 집 나비가 키보드를 밟으면서 실수로 상사에게 이상한 메시지를 전송했습니다."  # 재창작

        print(f"Original: {original}")
        print()

        # 테스트 1: 동일한 텍스트 (Fair Use 실패 예상)
        print("Test 1: Identical text")
        result1 = ai_rewriter.check_fair_use(
            original_text=original,
            generated_text=generated1
        )

        print(f"  Overall similarity: {result1['overall_similarity']:.1%}")
        print(f"  Structural: {result1['structural_similarity']:.1%}")
        print(f"  Lexical: {result1['lexical_similarity']:.1%}")
        print(f"  Semantic: {result1['semantic_similarity']:.1%}")
        print(f"  Fair Use: {'✓ Passed' if result1['is_fair_use'] else '✗ Failed'}")
        print(f"  Recommendation: {result1['recommendation']}")
        print()

        # 테스트 2: 재창작된 텍스트 (Fair Use 통과 예상)
        print("Test 2: Recreated text")
        result2 = ai_rewriter.check_fair_use(
            original_text=original,
            generated_text=generated2
        )

        print(f"  Overall similarity: {result2['overall_similarity']:.1%}")
        print(f"  Structural: {result2['structural_similarity']:.1%}")
        print(f"  Lexical: {result2['lexical_similarity']:.1%}")
        print(f"  Semantic: {result2['semantic_similarity']:.1%}")
        print(f"  Fair Use: {'✓ Passed' if result2['is_fair_use'] else '✗ Failed'}")
        print(f"  Recommendation: {result2['recommendation']}")
        print()

        print("✓ Similarity check completed")
        print()


def test_rewrite_with_feedback(app):
    """피드백 기반 재작성 테스트"""
    print("=" * 80)
    print("TEST 5: Rewrite with Feedback")
    print("=" * 80)
    print()

    with app.app_context():
        ai_rewriter = get_ai_rewriter()

        concept = "고양이가 키보드를 밟아서 이메일을 보냄"
        draft = "우리 집 고양이가 키보드 위에서 자다가 발로 키보드를 여러 번 밟았습니다. 그 바람에 상사에게 이상한 내용의 이메일이 전송되었습니다."
        feedback = "더 짧고 임팩트 있게 수정해주세요. 대화체로 바꿔주세요."

        print(f"Original concept: {concept}")
        print(f"Current draft: {draft}")
        print(f"Feedback: {feedback}")
        print()
        print("Rewriting with feedback...")
        print()

        result = ai_rewriter.rewrite_with_feedback(
            original_concept=concept,
            current_draft=draft,
            feedback=feedback
        )

        print(f"Revised draft:")
        print(f"  {result['revised_draft']}")
        print()
        print(f"Similarity to original concept: {result['similarity_to_original']:.1%}")
        print(f"Fair Use: {'✓' if result['is_fair_use'] else '✗'}")
        print(f"Original length: {result['metadata']['original_length']} chars")
        print(f"Revised length: {result['metadata']['revised_length']} chars")
        print(f"Length change: {result['metadata']['length_change']:+d} chars")
        print()

        print("✓ Rewrite with feedback completed")
        print()


def cleanup_test_data(app):
    """테스트 데이터 정리"""
    print("=" * 80)
    print("Cleaning up test data")
    print("=" * 80)
    print()

    with app.app_context():
        # 테스트 데이터 삭제
        User.query.filter_by(username='ai_test_user').delete()
        Source.query.filter_by(title='Test Source for AI').delete()

        db.session.commit()

        print("✓ Test data cleaned up")
        print()


def main():
    """메인 실행 함수"""
    print("\n")
    print("=" * 80)
    print("AI Assistant Test Suite")
    print("=" * 80)
    print("\n")

    app = create_app('development')

    try:
        # 테스트 데이터 생성
        user_id, inspiration_id = setup_test_data(app)
        input("Press Enter to continue to version generation test...")
        print("\n")

        # 1. 여러 버전 생성 테스트
        test_generate_versions(app)
        input("Press Enter to continue to paragraph improvement test...")
        print("\n")

        # 2. 문단 개선 테스트
        test_improve_paragraph(app)
        input("Press Enter to continue to title generation test...")
        print("\n")

        # 3. 제목 생성 테스트
        test_generate_titles(app)
        input("Press Enter to continue to similarity check test...")
        print("\n")

        # 4. 유사도 체크 테스트
        test_check_similarity(app)
        input("Press Enter to continue to feedback rewrite test...")
        print("\n")

        # 5. 피드백 기반 재작성 테스트
        test_rewrite_with_feedback(app)
        print("\n")

        # 정리
        cleanup_prompt = input("Clean up test data? (Y/n): ").strip().lower()
        if cleanup_prompt != 'n':
            cleanup_test_data(app)

        print("\n")
        print("=" * 80)
        print("All tests completed! ✅")
        print("=" * 80)
        print("\n")

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
