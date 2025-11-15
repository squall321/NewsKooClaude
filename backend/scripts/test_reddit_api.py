#!/usr/bin/env python3
"""
Reddit API 테스트 스크립트

PRAW 설정 및 Reddit 크롤러 기능을 테스트합니다.
"""
import os
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import create_app
from app.services.reddit_crawler import RedditCrawler
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()


def test_connection():
    """Reddit API 연결 테스트"""
    print("=" * 80)
    print("TEST 1: Reddit API Connection")
    print("=" * 80)
    print()

    client_id = os.getenv('REDDIT_CLIENT_ID')
    client_secret = os.getenv('REDDIT_CLIENT_SECRET')

    if not client_id or not client_secret:
        print("❌ Reddit API credentials not found")
        print("\nPlease set the following environment variables:")
        print("  REDDIT_CLIENT_ID - Your Reddit app client ID")
        print("  REDDIT_CLIENT_SECRET - Your Reddit app client secret")
        print("\nTo get credentials:")
        print("  1. Go to https://www.reddit.com/prefs/apps")
        print("  2. Create a new app (select 'script' type)")
        print("  3. Copy the client ID and secret")
        print("  4. Add them to your .env file or export them")
        return False

    print(f"Client ID: {client_id[:10]}... (hidden)")
    print(f"Client Secret: {'*' * 20}")
    print()

    crawler = RedditCrawler(
        client_id=client_id,
        client_secret=client_secret
    )

    if crawler.connect():
        print("✅ Successfully connected to Reddit API")
        print()
        return True
    else:
        print("❌ Failed to connect to Reddit API")
        print()
        return False


def test_fetch_posts(crawler):
    """게시물 가져오기 테스트"""
    print("=" * 80)
    print("TEST 2: Fetch Posts")
    print("=" * 80)
    print()

    subreddits = ['jokes', 'dadjokes', 'Showerthoughts']

    for subreddit in subreddits:
        print(f"--- Fetching from r/{subreddit} ---")

        posts = crawler.fetch_hot_posts(
            subreddit_name=subreddit,
            limit=5,
            time_filter='day'
        )

        print(f"Found {len(posts)} qualifying posts (score >= {crawler.MIN_SCORE}, comments >= {crawler.MIN_COMMENTS})")

        for i, post in enumerate(posts[:3], 1):  # 처음 3개만 출력
            print(f"\n{i}. {post.title[:70]}")
            print(f"   Author: u/{post.author}")
            print(f"   Score: {post.score:,} upvotes | Comments: {post.num_comments:,}")
            print(f"   URL: {post.permalink}")
            if post.is_self and post.selftext:
                preview = post.selftext[:100].replace('\n', ' ')
                if len(post.selftext) > 100:
                    preview += "..."
                print(f"   Preview: {preview}")

        print()


def test_save_to_database(crawler, app):
    """데이터베이스 저장 테스트"""
    print("=" * 80)
    print("TEST 3: Save to Database")
    print("=" * 80)
    print()

    with app.app_context():
        print("Fetching posts from r/jokes...")
        posts = crawler.fetch_hot_posts('jokes', limit=3)

        if not posts:
            print("❌ No posts found")
            return

        print(f"✓ Found {len(posts)} posts")
        print()

        for i, post in enumerate(posts, 1):
            print(f"{i}. Saving: {post.title[:50]}...")

            source = crawler.save_to_database(post, create_inspiration=True)

            if source:
                print(f"   ✓ Source ID: {source.id}")

                # Inspiration 확인
                from app.models import Inspiration
                inspiration = Inspiration.query.filter_by(source_id=source.id).first()
                if inspiration:
                    print(f"   ✓ Inspiration ID: {inspiration.id}")
                    print(f"   Concept preview: {inspiration.original_concept[:80]}...")
            else:
                print(f"   ⚠ Already exists or failed to save")

            print()


def test_batch_collection(crawler, app):
    """배치 수집 테스트"""
    print("=" * 80)
    print("TEST 4: Batch Collection")
    print("=" * 80)
    print()

    with app.app_context():
        print("Starting batch collection from multiple subreddits...")
        print()

        result = crawler.collect_from_subreddits(
            subreddit_names=['jokes', 'dadjokes'],
            limit_per_subreddit=5,
            time_filter='day',
            create_inspirations=True
        )

        print("=== Collection Results ===")
        print(f"Sources created: {result['sources_created']}")
        print(f"Inspirations created: {result['inspirations_created']}")
        print()


def test_statistics(crawler, app):
    """통계 조회 테스트"""
    print("=" * 80)
    print("TEST 5: Statistics")
    print("=" * 80)
    print()

    with app.app_context():
        stats = crawler.get_statistics()

        print("=== Reddit Collection Statistics ===")
        print(f"Total sources: {stats['total_sources']}")
        print(f"Total inspirations: {stats['total_inspirations']}")
        print(f"Collected in last 24h: {stats['recent_24h']}")
        print()

        if stats['subreddit_distribution']:
            print("Subreddit distribution:")
            for subreddit, count in sorted(
                stats['subreddit_distribution'].items(),
                key=lambda x: x[1],
                reverse=True
            ):
                print(f"  r/{subreddit}: {count}")
        else:
            print("No data collected yet")

        print()


def test_concept_summarization():
    """컨셉 요약 테스트"""
    print("=" * 80)
    print("TEST 6: Concept Summarization (Fair Use)")
    print("=" * 80)
    print()

    from app.services.reddit_crawler import RedditPostMetadata

    # 샘플 메타데이터
    sample_post = RedditPostMetadata(
        post_id='abc123',
        title='I told my wife she was drawing her eyebrows too high',
        url='https://reddit.com/r/jokes/abc123',
        author='funny_guy',
        subreddit='jokes',
        score=5420,
        num_comments=342,
        created_utc=1699999999,
        permalink='https://reddit.com/r/jokes/comments/abc123/eyebrows_joke',
        is_self=True,
        selftext='She looked surprised.'
    )

    client_id = os.getenv('REDDIT_CLIENT_ID', 'dummy')
    client_secret = os.getenv('REDDIT_CLIENT_SECRET', 'dummy')

    crawler = RedditCrawler(client_id, client_secret)
    concept = crawler._summarize_concept(sample_post)

    print("Original Post:")
    print(f"  Title: {sample_post.title}")
    print(f"  Selftext: {sample_post.selftext}")
    print()
    print("Summarized Concept (Fair Use):")
    print(concept)
    print()
    print("✓ Note: Only metadata is stored, not full content")
    print()


def main():
    """메인 실행 함수"""
    print("\n")
    print("=" * 80)
    print("Reddit API & Crawler Test Suite")
    print("=" * 80)
    print("\n")

    # 앱 생성
    app = create_app('development')

    try:
        # 1. 연결 테스트
        if not test_connection():
            print("\n⚠ Connection failed. Stopping tests.")
            print("\nPlease configure Reddit API credentials first:")
            print("  1. Create Reddit app at https://www.reddit.com/prefs/apps")
            print("  2. Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET in .env")
            return

        client_id = os.getenv('REDDIT_CLIENT_ID')
        client_secret = os.getenv('REDDIT_CLIENT_SECRET')

        crawler = RedditCrawler(client_id, client_secret)
        crawler.connect()

        input("Press Enter to continue to fetch posts test...")
        print("\n")

        # 2. 게시물 가져오기
        test_fetch_posts(crawler)
        input("Press Enter to continue to database save test...")
        print("\n")

        # 3. 데이터베이스 저장
        test_save_to_database(crawler, app)
        input("Press Enter to continue to batch collection test...")
        print("\n")

        # 4. 배치 수집
        test_batch_collection(crawler, app)
        input("Press Enter to continue to statistics test...")
        print("\n")

        # 5. 통계
        test_statistics(crawler, app)
        input("Press Enter to continue to concept summarization test...")
        print("\n")

        # 6. 컨셉 요약
        test_concept_summarization()

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
