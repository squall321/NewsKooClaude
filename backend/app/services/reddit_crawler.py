"""
Reddit 영감 수집 크롤러

PRAW를 사용하여 Reddit의 유머 subreddit에서 메타데이터만 수집합니다.
Fair Use를 준수하기 위해 전문 복사는 하지 않고, URL과 요약만 저장합니다.
"""
import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import praw
from praw.models import Submission

from app.models import Source, Inspiration
from app import db

logger = logging.getLogger(__name__)


@dataclass
class RedditPostMetadata:
    """Reddit 게시물 메타데이터"""
    post_id: str
    title: str
    url: str
    author: str
    subreddit: str
    score: int  # upvotes - downvotes
    num_comments: int
    created_utc: float
    permalink: str
    is_self: bool  # 텍스트 게시물 여부
    selftext: Optional[str]  # 텍스트 게시물 내용 (요약용, 저장 안함)


class RedditCrawler:
    """
    Reddit 크롤러 서비스

    PRAW를 사용하여 지정된 subreddit에서 인기 있는 유머 콘텐츠의
    메타데이터를 수집하고 Source 및 Inspiration 객체를 생성합니다.
    """

    # 기본 타겟 subreddit 목록
    DEFAULT_SUBREDDITS = [
        'funny',
        'Jokes',
        'dadjokes',
        'cleanjokes',
        'Showerthoughts',
        'AmItheAsshole',  # 상황 유머
        'tifu',  # Today I F***ed Up
        'ContagiousLaughter',
    ]

    # Fair Use 준수: 최소 인기도 기준
    MIN_SCORE = 100  # 최소 100 upvotes
    MIN_COMMENTS = 10  # 최소 10 comments

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        user_agent: str = "NewsKoo/1.0"
    ):
        """
        Args:
            client_id: Reddit API client ID
            client_secret: Reddit API client secret
            user_agent: User agent string
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_agent = user_agent

        self.reddit: Optional[praw.Reddit] = None

    def connect(self) -> bool:
        """
        Reddit API에 연결

        Returns:
            연결 성공 여부
        """
        try:
            self.reddit = praw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                user_agent=self.user_agent,
                check_for_async=False
            )

            # 연결 테스트
            _ = self.reddit.user.me()  # 인증되면 None 반환 (read-only)

            logger.info("Successfully connected to Reddit API")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to Reddit API: {e}")
            self.reddit = None
            return False

    def is_connected(self) -> bool:
        """연결 상태 확인"""
        return self.reddit is not None

    def fetch_hot_posts(
        self,
        subreddit_name: str,
        limit: int = 25,
        time_filter: str = 'day'
    ) -> List[RedditPostMetadata]:
        """
        특정 subreddit에서 인기 게시물 가져오기

        Args:
            subreddit_name: Subreddit 이름
            limit: 가져올 게시물 수
            time_filter: 시간 필터 ('hour', 'day', 'week', 'month', 'year', 'all')

        Returns:
            RedditPostMetadata 리스트
        """
        if not self.is_connected():
            logger.error("Not connected to Reddit API")
            return []

        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            posts = []

            # hot 또는 top 게시물 가져오기
            if time_filter == 'hot':
                submissions = subreddit.hot(limit=limit)
            else:
                submissions = subreddit.top(time_filter=time_filter, limit=limit)

            for submission in submissions:
                # 메타데이터 추출
                metadata = self._extract_metadata(submission)

                # 필터링: 최소 인기도
                if metadata.score >= self.MIN_SCORE and metadata.num_comments >= self.MIN_COMMENTS:
                    posts.append(metadata)

            logger.info(f"Fetched {len(posts)} posts from r/{subreddit_name}")
            return posts

        except Exception as e:
            logger.error(f"Error fetching posts from r/{subreddit_name}: {e}")
            return []

    def _extract_metadata(self, submission: Submission) -> RedditPostMetadata:
        """
        Submission 객체에서 메타데이터 추출

        Args:
            submission: PRAW Submission 객체

        Returns:
            RedditPostMetadata
        """
        return RedditPostMetadata(
            post_id=submission.id,
            title=submission.title,
            url=submission.url,
            author=str(submission.author) if submission.author else '[deleted]',
            subreddit=str(submission.subreddit),
            score=submission.score,
            num_comments=submission.num_comments,
            created_utc=submission.created_utc,
            permalink=f"https://reddit.com{submission.permalink}",
            is_self=submission.is_self,
            selftext=submission.selftext if submission.is_self else None
        )

    def save_to_database(
        self,
        metadata: RedditPostMetadata,
        create_inspiration: bool = True
    ) -> Optional[Source]:
        """
        메타데이터를 Source (및 Inspiration) 객체로 저장

        Args:
            metadata: Reddit 메타데이터
            create_inspiration: Inspiration 객체도 생성할지 여부

        Returns:
            생성된 Source 객체 (실패 시 None)
        """
        try:
            # 중복 체크
            existing = Source.query.filter_by(
                platform='reddit',
                source_id=metadata.post_id
            ).first()

            if existing:
                logger.debug(f"Source already exists: {metadata.post_id}")
                return existing

            # Source 생성
            source = Source.create(
                platform='reddit',
                source_url=metadata.permalink,
                source_id=metadata.post_id,
                title=metadata.title,
                author=metadata.author,
                metadata_json={
                    'subreddit': metadata.subreddit,
                    'score': metadata.score,
                    'num_comments': metadata.num_comments,
                    'created_utc': metadata.created_utc,
                    'is_self': metadata.is_self,
                    'url': metadata.url  # 외부 링크 (이미지, 동영상 등)
                }
            )

            db.session.commit()
            logger.info(f"Created Source: {source.id} ({metadata.title[:50]}...)")

            # Inspiration 생성 (선택)
            if create_inspiration:
                inspiration = self._create_inspiration_from_source(source, metadata)
                if inspiration:
                    logger.info(f"Created Inspiration: {inspiration.id}")

            return source

        except Exception as e:
            logger.error(f"Failed to save source: {e}")
            db.session.rollback()
            return None

    def _create_inspiration_from_source(
        self,
        source: Source,
        metadata: RedditPostMetadata
    ) -> Optional[Inspiration]:
        """
        Source로부터 Inspiration 생성

        원본 텍스트는 저장하지 않고, 핵심 컨셉만 추출합니다.

        Args:
            source: Source 객체
            metadata: Reddit 메타데이터

        Returns:
            생성된 Inspiration (실패 시 None)
        """
        try:
            # 원본 컨셉 요약 (Fair Use)
            original_concept = self._summarize_concept(metadata)

            # Inspiration 생성
            inspiration = Inspiration.create(
                source_id=source.id,
                original_concept=original_concept,
                status='collected'
            )

            db.session.commit()
            return inspiration

        except Exception as e:
            logger.error(f"Failed to create inspiration: {e}")
            db.session.rollback()
            return None

    def _summarize_concept(self, metadata: RedditPostMetadata) -> str:
        """
        메타데이터로부터 핵심 컨셉 요약

        Fair Use를 위해 직접 복사는 하지 않고 핵심 아이디어만 추출합니다.

        Args:
            metadata: Reddit 메타데이터

        Returns:
            요약된 컨셉
        """
        # 제목 기반 컨셉
        concept_parts = [f"Title: {metadata.title}"]

        # Subreddit 컨텍스트
        concept_parts.append(f"Context: r/{metadata.subreddit}")

        # 텍스트 게시물이면 첫 200자만 (컨셉 이해용)
        if metadata.is_self and metadata.selftext:
            preview = metadata.selftext[:200].replace('\n', ' ').strip()
            if len(metadata.selftext) > 200:
                preview += "..."
            concept_parts.append(f"Preview: {preview}")

        # 인기도
        concept_parts.append(f"Popularity: {metadata.score} upvotes, {metadata.num_comments} comments")

        return "\n".join(concept_parts)

    def collect_from_subreddits(
        self,
        subreddit_names: Optional[List[str]] = None,
        limit_per_subreddit: int = 10,
        time_filter: str = 'day',
        create_inspirations: bool = True
    ) -> Dict[str, int]:
        """
        여러 subreddit에서 배치 수집

        Args:
            subreddit_names: Subreddit 목록 (None이면 기본 목록)
            limit_per_subreddit: subreddit당 수집 개수
            time_filter: 시간 필터
            create_inspirations: Inspiration도 생성할지 여부

        Returns:
            {'sources_created': N, 'inspirations_created': M}
        """
        if not self.is_connected():
            if not self.connect():
                logger.error("Failed to connect to Reddit")
                return {'sources_created': 0, 'inspirations_created': 0}

        subreddits = subreddit_names or self.DEFAULT_SUBREDDITS

        sources_created = 0
        inspirations_created = 0

        for subreddit_name in subreddits:
            logger.info(f"Collecting from r/{subreddit_name}...")

            # 게시물 가져오기
            posts = self.fetch_hot_posts(
                subreddit_name=subreddit_name,
                limit=limit_per_subreddit,
                time_filter=time_filter
            )

            # 저장
            for post in posts:
                source = self.save_to_database(
                    post,
                    create_inspiration=create_inspirations
                )

                if source:
                    sources_created += 1

                    if create_inspirations:
                        # Inspiration이 생성되었는지 확인
                        if Inspiration.query.filter_by(source_id=source.id).first():
                            inspirations_created += 1

        logger.info(
            f"Collection complete: {sources_created} sources, "
            f"{inspirations_created} inspirations"
        )

        return {
            'sources_created': sources_created,
            'inspirations_created': inspirations_created
        }

    def get_statistics(self) -> Dict[str, Any]:
        """
        수집 통계 조회

        Returns:
            통계 딕셔너리
        """
        total_sources = Source.query.filter_by(platform='reddit').count()
        total_inspirations = Inspiration.query.join(Source).filter(
            Source.platform == 'reddit'
        ).count()

        # 최근 24시간 수집량
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_sources = Source.query.filter(
            Source.platform == 'reddit',
            Source.created_at >= yesterday
        ).count()

        # Subreddit별 분포
        subreddit_dist = db.session.query(
            db.func.json_extract(Source.metadata_json, '$.subreddit').label('subreddit'),
            db.func.count().label('count')
        ).filter(
            Source.platform == 'reddit'
        ).group_by('subreddit').all()

        return {
            'total_sources': total_sources,
            'total_inspirations': total_inspirations,
            'recent_24h': recent_sources,
            'subreddit_distribution': {
                sub: count for sub, count in subreddit_dist if sub
            }
        }


# 테스트용 함수
def test_reddit_crawler():
    """RedditCrawler 테스트"""
    import os
    from app import create_app

    client_id = os.getenv('REDDIT_CLIENT_ID')
    client_secret = os.getenv('REDDIT_CLIENT_SECRET')

    if not client_id or not client_secret:
        print("❌ Reddit API credentials not found in environment")
        print("Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET")
        return

    app = create_app('development')

    with app.app_context():
        crawler = RedditCrawler(
            client_id=client_id,
            client_secret=client_secret
        )

        # 연결 테스트
        if crawler.connect():
            print("✓ Connected to Reddit API")

            # 게시물 가져오기 테스트
            posts = crawler.fetch_hot_posts('jokes', limit=5)
            print(f"\n✓ Fetched {len(posts)} posts from r/jokes:")

            for i, post in enumerate(posts, 1):
                print(f"\n{i}. {post.title[:60]}...")
                print(f"   Score: {post.score}, Comments: {post.num_comments}")
                print(f"   URL: {post.permalink}")

            # 통계
            stats = crawler.get_statistics()
            print(f"\n=== Statistics ===")
            print(f"Total sources: {stats['total_sources']}")
            print(f"Total inspirations: {stats['total_inspirations']}")
            print(f"Recent (24h): {stats['recent_24h']}")

        else:
            print("❌ Failed to connect to Reddit API")


if __name__ == "__main__":
    test_reddit_crawler()
