"""
스케줄링 서비스

APScheduler를 사용하여 주기적 작업을 관리합니다.
- Reddit 크롤링
- 콘텐츠 생성
- 데이터 정리
"""
import logging
from typing import Optional, Dict, List, Any
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.job import Job
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

from app import db
from app.services.reddit_crawler import RedditCrawler
from app.config import Settings

logger = logging.getLogger(__name__)


class SchedulerService:
    """
    스케줄링 서비스

    APScheduler를 사용하여 주기적 작업을 스케줄링하고 관리합니다.
    """

    def __init__(self, app=None):
        """
        Args:
            app: Flask app instance (선택)
        """
        self.scheduler: Optional[BackgroundScheduler] = None
        self.app = app
        self._job_history: List[Dict[str, Any]] = []
        self._max_history = 100  # 최대 기록 보관 개수

        if app:
            self.init_app(app)

    def init_app(self, app):
        """
        Flask 앱 초기화

        Args:
            app: Flask app instance
        """
        self.app = app

        # 스케줄러 생성
        self.scheduler = BackgroundScheduler(
            timezone='Asia/Seoul',
            job_defaults={
                'coalesce': True,  # 누적된 작업을 하나로 병합
                'max_instances': 1,  # 동시 실행 방지
                'misfire_grace_time': 900  # 15분 지연 허용
            }
        )

        # 이벤트 리스너 등록
        self.scheduler.add_listener(
            self._job_executed_listener,
            EVENT_JOB_EXECUTED | EVENT_JOB_ERROR
        )

        # 기본 작업 등록
        self._register_default_jobs()

        logger.info("Scheduler service initialized")

    def _job_executed_listener(self, event):
        """
        작업 실행 이벤트 리스너

        Args:
            event: APScheduler JobExecutionEvent
        """
        job_id = event.job_id
        execution_time = datetime.now()

        if event.exception:
            # 에러 발생
            logger.error(
                f"Job {job_id} failed at {execution_time}: {event.exception}"
            )
            status = 'failed'
            error_message = str(event.exception)
        else:
            # 성공
            logger.info(f"Job {job_id} completed at {execution_time}")
            status = 'success'
            error_message = None

        # 히스토리 기록
        self._add_to_history(
            job_id=job_id,
            status=status,
            execution_time=execution_time,
            error_message=error_message,
            return_value=event.retval if not event.exception else None
        )

    def _add_to_history(
        self,
        job_id: str,
        status: str,
        execution_time: datetime,
        error_message: Optional[str] = None,
        return_value: Any = None
    ):
        """
        작업 히스토리 추가

        Args:
            job_id: Job ID
            status: 상태 ('success', 'failed')
            execution_time: 실행 시간
            error_message: 에러 메시지 (실패 시)
            return_value: 반환 값 (성공 시)
        """
        history_entry = {
            'job_id': job_id,
            'status': status,
            'execution_time': execution_time.isoformat(),
            'error_message': error_message,
            'return_value': return_value
        }

        self._job_history.append(history_entry)

        # 최대 개수 초과 시 오래된 것 삭제
        if len(self._job_history) > self._max_history:
            self._job_history = self._job_history[-self._max_history:]

    def _register_default_jobs(self):
        """기본 작업 등록"""
        # Reddit 크롤링 (하루 2회: 오전 9시, 오후 9시)
        self.add_job(
            func=self._reddit_collection_job,
            trigger='cron',
            hour='9,21',  # 09:00, 21:00
            minute='0',
            job_id='reddit_collection',
            name='Reddit Inspiration Collection',
            replace_existing=True
        )

        logger.info("Default jobs registered")

    def _reddit_collection_job(self) -> Dict[str, Any]:
        """
        Reddit 수집 작업

        Returns:
            작업 결과 딕셔너리
        """
        logger.info("Starting Reddit collection job...")

        try:
            # Flask app context 필요
            with self.app.app_context():
                # Reddit 크롤러 생성
                settings = Settings()
                crawler = RedditCrawler(
                    client_id=settings.REDDIT_CLIENT_ID,
                    client_secret=settings.REDDIT_CLIENT_SECRET
                )

                # 연결
                if not crawler.connect():
                    raise Exception("Failed to connect to Reddit API")

                # 배치 수집
                result = crawler.collect_from_subreddits(
                    subreddit_names=None,  # 기본 subreddit 사용
                    limit_per_subreddit=10,
                    time_filter='day',
                    create_inspirations=True
                )

                logger.info(
                    f"Reddit collection completed: "
                    f"{result['sources_created']} sources, "
                    f"{result['inspirations_created']} inspirations"
                )

                return {
                    'success': True,
                    'sources_created': result['sources_created'],
                    'inspirations_created': result['inspirations_created'],
                    'timestamp': datetime.now().isoformat()
                }

        except Exception as e:
            logger.error(f"Reddit collection job failed: {e}", exc_info=True)
            raise

    def start(self):
        """스케줄러 시작"""
        if self.scheduler and not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler started")

    def shutdown(self, wait: bool = True):
        """
        스케줄러 종료

        Args:
            wait: 실행 중인 작업 완료 대기 여부
        """
        if self.scheduler and self.scheduler.running:
            self.scheduler.shutdown(wait=wait)
            logger.info("Scheduler shut down")

    def add_job(
        self,
        func,
        trigger: str,
        job_id: str,
        name: str,
        replace_existing: bool = False,
        **trigger_kwargs
    ) -> Optional[Job]:
        """
        작업 추가

        Args:
            func: 실행할 함수
            trigger: 트리거 타입 ('cron', 'interval', 'date')
            job_id: Job ID (유니크)
            name: Job 이름
            replace_existing: 기존 작업 교체 여부
            **trigger_kwargs: 트리거 파라미터 (hour, minute 등)

        Returns:
            Job 객체 (실패 시 None)
        """
        if not self.scheduler:
            logger.error("Scheduler not initialized")
            return None

        try:
            # 트리거 생성
            if trigger == 'cron':
                trigger_obj = CronTrigger(**trigger_kwargs)
            elif trigger == 'interval':
                trigger_obj = IntervalTrigger(**trigger_kwargs)
            else:
                raise ValueError(f"Unsupported trigger type: {trigger}")

            # 작업 추가
            job = self.scheduler.add_job(
                func=func,
                trigger=trigger_obj,
                id=job_id,
                name=name,
                replace_existing=replace_existing
            )

            logger.info(f"Job added: {job_id} ({name})")
            return job

        except Exception as e:
            logger.error(f"Failed to add job {job_id}: {e}")
            return None

    def remove_job(self, job_id: str) -> bool:
        """
        작업 제거

        Args:
            job_id: Job ID

        Returns:
            성공 여부
        """
        if not self.scheduler:
            return False

        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Job removed: {job_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to remove job {job_id}: {e}")
            return False

    def pause_job(self, job_id: str) -> bool:
        """
        작업 일시 정지

        Args:
            job_id: Job ID

        Returns:
            성공 여부
        """
        if not self.scheduler:
            return False

        try:
            self.scheduler.pause_job(job_id)
            logger.info(f"Job paused: {job_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to pause job {job_id}: {e}")
            return False

    def resume_job(self, job_id: str) -> bool:
        """
        작업 재개

        Args:
            job_id: Job ID

        Returns:
            성공 여부
        """
        if not self.scheduler:
            return False

        try:
            self.scheduler.resume_job(job_id)
            logger.info(f"Job resumed: {job_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to resume job {job_id}: {e}")
            return False

    def run_job_now(self, job_id: str) -> bool:
        """
        작업 즉시 실행

        Args:
            job_id: Job ID

        Returns:
            성공 여부
        """
        if not self.scheduler:
            return False

        try:
            job = self.scheduler.get_job(job_id)
            if not job:
                logger.error(f"Job not found: {job_id}")
                return False

            job.modify(next_run_time=datetime.now())
            logger.info(f"Job scheduled to run now: {job_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to run job {job_id}: {e}")
            return False

    def get_jobs(self) -> List[Dict[str, Any]]:
        """
        모든 작업 조회

        Returns:
            작업 정보 리스트
        """
        if not self.scheduler:
            return []

        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger),
                'pending': job.pending
            })

        return jobs

    def get_job_history(
        self,
        job_id: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        작업 히스토리 조회

        Args:
            job_id: Job ID (None이면 전체)
            limit: 최대 개수

        Returns:
            히스토리 리스트 (최신순)
        """
        history = self._job_history

        # 필터링
        if job_id:
            history = [h for h in history if h['job_id'] == job_id]

        # 최신순 정렬 및 제한
        history = sorted(
            history,
            key=lambda x: x['execution_time'],
            reverse=True
        )[:limit]

        return history

    def get_statistics(self) -> Dict[str, Any]:
        """
        스케줄러 통계

        Returns:
            통계 딕셔너리
        """
        if not self.scheduler:
            return {
                'running': False,
                'total_jobs': 0,
                'active_jobs': 0
            }

        jobs = self.scheduler.get_jobs()

        # 최근 24시간 실행 횟수
        from datetime import timedelta
        yesterday = datetime.now() - timedelta(days=1)

        recent_executions = [
            h for h in self._job_history
            if datetime.fromisoformat(h['execution_time']) >= yesterday
        ]

        success_count = sum(1 for h in recent_executions if h['status'] == 'success')
        failed_count = sum(1 for h in recent_executions if h['status'] == 'failed')

        return {
            'running': self.scheduler.running,
            'total_jobs': len(jobs),
            'active_jobs': sum(1 for j in jobs if not j.pending),
            'recent_24h': {
                'total': len(recent_executions),
                'success': success_count,
                'failed': failed_count
            }
        }


# 글로벌 스케줄러 인스턴스
_scheduler_instance: Optional[SchedulerService] = None


def init_scheduler(app) -> SchedulerService:
    """
    스케줄러 초기화 (Flask 앱 시작 시 호출)

    Args:
        app: Flask app instance

    Returns:
        SchedulerService 인스턴스
    """
    global _scheduler_instance

    if _scheduler_instance is None:
        _scheduler_instance = SchedulerService(app)
        _scheduler_instance.start()

    return _scheduler_instance


def get_scheduler() -> Optional[SchedulerService]:
    """
    글로벌 스케줄러 인스턴스 반환

    Returns:
        SchedulerService 인스턴스 (초기화 안되었으면 None)
    """
    return _scheduler_instance
