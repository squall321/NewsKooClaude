#!/usr/bin/env python3
"""
Inspiration API 테스트 스크립트

Inspiration 관리 기능을 테스트합니다.
"""
import os
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import create_app, db
from app.models import User, Source, Inspiration
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()


def setup_test_data(app):
    """테스트 데이터 생성"""
    print("=== Setting up test data ===\n")

    with app.app_context():
        # 기존 테스트 데이터 삭제
        User.query.filter_by(username='inspiration_tester').delete()
        Source.query.filter_by(title='Test Source for Inspiration').delete()

        # 사용자 생성
        user = User.create(
            username='inspiration_tester',
            email='inspiration_tester@example.com',
            password='test1234',
            role='editor'
        )
        user_id = user.id

        # 소스 생성
        source = Source.create(
            platform='reddit',
            source_id='test_insp_123',
            url='https://reddit.com/r/funny/test',
            title='Test Source for Inspiration',
            author='test_author',
            upvotes=1500,
            comments=150
        )

        # Inspiration 생성
        inspiration = Inspiration.create(
            source_id=source.id,
            concept='고양이가 키보드 위에서 자다가 실수로 이메일 전송',
            similarity_score=0.65,
            status='pending'
        )

        db.session.commit()

        print(f"✓ Test user created: {user.username} (ID: {user_id})")
        print(f"✓ Test source created: {source.title} (ID: {source.id})")
        print(f"✓ Test inspiration created: {inspiration.concept[:50]}... (ID: {inspiration.id})")
        print()

        return user_id, inspiration.id


def test_list_inspirations(app):
    """Inspiration 목록 조회 테스트"""
    print("=" * 80)
    print("TEST 1: List Inspirations")
    print("=" * 80)
    print()

    with app.app_context():
        inspirations = Inspiration.query.all()

        print(f"Total inspirations: {len(inspirations)}")
        for insp in inspirations:
            print(f"  - {insp.concept[:50]}... (Status: {insp.status})")
        print()

        print("✓ List test completed")
        print()


def test_approve_inspiration(app, inspiration_id):
    """Inspiration 승인 테스트"""
    print("=" * 80)
    print("TEST 2: Approve Inspiration")
    print("=" * 80)
    print()

    with app.app_context():
        inspiration = Inspiration.query.get(inspiration_id)

        print(f"Original status: {inspiration.status}")

        inspiration.status = 'approved'
        db.session.commit()

        print(f"New status: {inspiration.status}")
        print()

        print("✓ Approve test completed")
        print()


def test_statistics(app):
    """통계 조회 테스트"""
    print("=" * 80)
    print("TEST 3: Statistics")
    print("=" * 80)
    print()

    with app.app_context():
        from sqlalchemy import func

        total = Inspiration.query.count()

        by_status = {}
        for status in ['pending', 'approved', 'rejected', 'used']:
            count = Inspiration.query.filter_by(status=status).count()
            by_status[status] = count

        avg_similarity = db.session.query(
            func.avg(Inspiration.similarity_score)
        ).scalar() or 0.0

        print(f"Total inspirations: {total}")
        print(f"By status: {by_status}")
        print(f"Average similarity: {avg_similarity:.2%}")
        print()

        print("✓ Statistics test completed")
        print()


def cleanup_test_data(app):
    """테스트 데이터 정리"""
    print("=" * 80)
    print("Cleaning up test data")
    print("=" * 80)
    print()

    with app.app_context():
        User.query.filter_by(username='inspiration_tester').delete()
        Source.query.filter_by(title='Test Source for Inspiration').delete()

        db.session.commit()

        print("✓ Test data cleaned up")
        print()


def main():
    """메인 실행 함수"""
    print("\n")
    print("=" * 80)
    print("Inspiration API Test Suite")
    print("=" * 80)
    print("\n")

    app = create_app('development')

    try:
        # 테스트 데이터 생성
        user_id, inspiration_id = setup_test_data(app)
        input("Press Enter to continue to list test...")
        print("\n")

        # 1. 목록 조회 테스트
        test_list_inspirations(app)
        input("Press Enter to continue to approve test...")
        print("\n")

        # 2. 승인 테스트
        test_approve_inspiration(app, inspiration_id)
        input("Press Enter to continue to statistics test...")
        print("\n")

        # 3. 통계 테스트
        test_statistics(app)
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
