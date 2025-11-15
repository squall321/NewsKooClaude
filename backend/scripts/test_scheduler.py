#!/usr/bin/env python3
"""
스케줄러 테스트 스크립트

APScheduler 및 작업 관리 기능을 테스트합니다.
"""
import os
import sys
import time
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import create_app
from app.services.scheduler import SchedulerService
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()


def test_scheduler_initialization():
    """스케줄러 초기화 테스트"""
    print("=" * 80)
    print("TEST 1: Scheduler Initialization")
    print("=" * 80)
    print()

    app = create_app('development')

    with app.app_context():
        scheduler = SchedulerService(app)

        print(f"Scheduler created: {scheduler is not None}")
        print(f"Scheduler running: {scheduler.scheduler.running if scheduler.scheduler else False}")
        print()

        # 시작
        scheduler.start()
        print(f"Scheduler started: {scheduler.scheduler.running}")
        print()

        # 통계
        stats = scheduler.get_statistics()
        print("=== Statistics ===")
        print(f"Running: {stats['running']}")
        print(f"Total jobs: {stats['total_jobs']}")
        print(f"Active jobs: {stats['active_jobs']}")
        print()

        # 종료
        scheduler.shutdown(wait=False)
        print("Scheduler shut down")
        print()

        return scheduler


def test_job_management(app):
    """작업 관리 테스트"""
    print("=" * 80)
    print("TEST 2: Job Management")
    print("=" * 80)
    print()

    with app.app_context():
        scheduler = SchedulerService(app)
        scheduler.start()

        # 작업 목록 조회
        jobs = scheduler.get_jobs()
        print(f"Default jobs registered: {len(jobs)}")
        for job in jobs:
            print(f"  - {job['id']}: {job['name']}")
            print(f"    Next run: {job['next_run_time']}")
            print(f"    Trigger: {job['trigger']}")
        print()

        # 테스트 작업 추가
        def test_job():
            print("Test job executed!")
            return {'result': 'success'}

        job = scheduler.add_job(
            func=test_job,
            trigger='interval',
            seconds=5,
            job_id='test_job',
            name='Test Job',
            replace_existing=True
        )

        if job:
            print(f"✓ Test job added: {job.id}")
        else:
            print("✗ Failed to add test job")
        print()

        # 작업 목록 재조회
        jobs = scheduler.get_jobs()
        print(f"Total jobs after adding: {len(jobs)}")
        print()

        # 작업 즉시 실행
        print("Running test job now...")
        success = scheduler.run_job_now('test_job')
        print(f"Run now: {'✓' if success else '✗'}")
        print()

        # 잠시 대기 (작업 실행 확인)
        time.sleep(2)

        # 히스토리 확인
        history = scheduler.get_job_history(job_id='test_job', limit=5)
        print(f"Job history: {len(history)} executions")
        for h in history:
            print(f"  - {h['execution_time']}: {h['status']}")
            if h['return_value']:
                print(f"    Return: {h['return_value']}")
        print()

        # 작업 일시 정지
        print("Pausing test job...")
        scheduler.pause_job('test_job')
        print()

        # 작업 재개
        print("Resuming test job...")
        scheduler.resume_job('test_job')
        print()

        # 작업 제거
        print("Removing test job...")
        scheduler.remove_job('test_job')
        jobs = scheduler.get_jobs()
        print(f"Total jobs after removal: {len(jobs)}")
        print()

        scheduler.shutdown(wait=False)


def test_reddit_collection_job(app):
    """Reddit 수집 작업 테스트"""
    print("=" * 80)
    print("TEST 3: Reddit Collection Job")
    print("=" * 80)
    print()

    client_id = os.getenv('REDDIT_CLIENT_ID')
    client_secret = os.getenv('REDDIT_CLIENT_SECRET')

    if not client_id or not client_secret:
        print("⚠ Reddit API credentials not found")
        print("Skipping Reddit collection test")
        print()
        return

    with app.app_context():
        scheduler = SchedulerService(app)
        scheduler.start()

        # Reddit 수집 작업 확인
        jobs = scheduler.get_jobs()
        reddit_job = next((j for j in jobs if j['id'] == 'reddit_collection'), None)

        if reddit_job:
            print("✓ Reddit collection job found")
            print(f"  Name: {reddit_job['name']}")
            print(f"  Next run: {reddit_job['next_run_time']}")
            print(f"  Trigger: {reddit_job['trigger']}")
            print()

            # 즉시 실행 (선택)
            run_now = input("Run Reddit collection now? (y/N): ").strip().lower()
            if run_now == 'y':
                print("\nRunning Reddit collection job...")
                print("This may take 30-60 seconds...")
                scheduler.run_job_now('reddit_collection')

                # 완료 대기
                time.sleep(5)

                # 히스토리 확인
                history = scheduler.get_job_history(job_id='reddit_collection', limit=1)
                if history:
                    latest = history[0]
                    print(f"\n=== Latest Execution ===")
                    print(f"Time: {latest['execution_time']}")
                    print(f"Status: {latest['status']}")
                    if latest['status'] == 'success' and latest['return_value']:
                        result = latest['return_value']
                        print(f"Sources created: {result.get('sources_created', 0)}")
                        print(f"Inspirations created: {result.get('inspirations_created', 0)}")
                    elif latest['status'] == 'failed':
                        print(f"Error: {latest['error_message']}")
        else:
            print("✗ Reddit collection job not found")

        print()
        scheduler.shutdown(wait=False)


def test_scheduler_statistics(app):
    """스케줄러 통계 테스트"""
    print("=" * 80)
    print("TEST 4: Scheduler Statistics")
    print("=" * 80)
    print()

    with app.app_context():
        scheduler = SchedulerService(app)
        scheduler.start()

        # 테스트 작업 추가 및 실행
        def dummy_job():
            return {'message': 'dummy'}

        scheduler.add_job(
            func=dummy_job,
            trigger='interval',
            seconds=1,
            job_id='dummy_job',
            name='Dummy Job'
        )

        # 여러 번 실행
        print("Executing dummy job 3 times...")
        for i in range(3):
            scheduler.run_job_now('dummy_job')
            time.sleep(1)

        # 통계 조회
        stats = scheduler.get_statistics()
        print("\n=== Scheduler Statistics ===")
        print(f"Running: {stats['running']}")
        print(f"Total jobs: {stats['total_jobs']}")
        print(f"Active jobs: {stats['active_jobs']}")
        print(f"\nRecent 24h:")
        print(f"  Total executions: {stats['recent_24h']['total']}")
        print(f"  Success: {stats['recent_24h']['success']}")
        print(f"  Failed: {stats['recent_24h']['failed']}")
        print()

        scheduler.shutdown(wait=False)


def main():
    """메인 실행 함수"""
    print("\n")
    print("=" * 80)
    print("Scheduler Test Suite")
    print("=" * 80)
    print("\n")

    app = create_app('development')

    try:
        # 1. 초기화 테스트
        test_scheduler_initialization()
        input("Press Enter to continue to job management test...")
        print("\n")

        # 2. 작업 관리 테스트
        test_job_management(app)
        input("Press Enter to continue to Reddit collection test...")
        print("\n")

        # 3. Reddit 수집 작업 테스트
        test_reddit_collection_job(app)
        input("Press Enter to continue to statistics test...")
        print("\n")

        # 4. 통계 테스트
        test_scheduler_statistics(app)

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
