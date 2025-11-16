"""
성능 모니터링 유틸리티
"""

import time
import functools
import logging
from flask import g, request
from datetime import datetime

logger = logging.getLogger(__name__)


def measure_time(func):
    """함수 실행 시간 측정 데코레이터"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()

        execution_time = (end_time - start_time) * 1000  # ms

        logger.info(f'{func.__name__} executed in {execution_time:.2f}ms')

        # Flask g 객체에 저장 (응답 헤더에 추가 가능)
        if hasattr(g, 'execution_times'):
            g.execution_times[func.__name__] = execution_time
        else:
            g.execution_times = {func.__name__: execution_time}

        return result

    return wrapper


def measure_query_performance(func):
    """데이터베이스 쿼리 성능 측정"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        from app import db

        # 쿼리 수 측정 시작
        start_query_count = len(db.session.query(db.text('1')).all())
        start_time = time.time()

        result = func(*args, **kwargs)

        end_time = time.time()
        end_query_count = len(db.session.query(db.text('1')).all())

        execution_time = (end_time - start_time) * 1000
        query_count = end_query_count - start_query_count

        logger.info(
            f'{func.__name__}: {execution_time:.2f}ms, '
            f'{query_count} queries'
        )

        return result

    return wrapper


class PerformanceMonitor:
    """성능 모니터링 컨텍스트 매니저"""

    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None
        self.end_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        duration = (self.end_time - self.start_time) * 1000

        if exc_type is None:
            logger.info(f'{self.operation_name} completed in {duration:.2f}ms')
        else:
            logger.error(
                f'{self.operation_name} failed after {duration:.2f}ms: '
                f'{exc_type.__name__}: {exc_val}'
            )

    @property
    def duration(self):
        """실행 시간 (ms)"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time) * 1000
        return None


# 요청별 성능 추적
def init_request_monitoring(app):
    """Flask 요청 모니터링 초기화"""

    @app.before_request
    def before_request():
        g.start_time = time.time()
        g.request_id = generate_request_id()

    @app.after_request
    def after_request(response):
        if hasattr(g, 'start_time'):
            duration = (time.time() - g.start_time) * 1000

            # 응답 헤더에 실행 시간 추가
            response.headers['X-Response-Time'] = f'{duration:.2f}ms'

            # 요청 ID 추가
            if hasattr(g, 'request_id'):
                response.headers['X-Request-ID'] = g.request_id

            # 느린 요청 경고 (500ms 이상)
            if duration > 500:
                logger.warning(
                    f'Slow request: {request.method} {request.path} '
                    f'took {duration:.2f}ms'
                )

            # 요청 로그
            logger.info(
                f'{request.method} {request.path} '
                f'{response.status_code} {duration:.2f}ms'
            )

        return response

    return app


def generate_request_id():
    """고유 요청 ID 생성"""
    import uuid
    return str(uuid.uuid4())[:8]


# 메모리 사용량 추적
def log_memory_usage(prefix=''):
    """메모리 사용량 로깅"""
    try:
        import psutil
        import os

        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / 1024 / 1024

        logger.info(f'{prefix}Memory usage: {memory_mb:.2f} MB')
    except ImportError:
        logger.warning('psutil not installed, cannot log memory usage')


# 캐시 성능 추적
class CachePerformanceTracker:
    """캐시 적중률 추적"""

    def __init__(self):
        self.hits = 0
        self.misses = 0

    def record_hit(self):
        self.hits += 1

    def record_miss(self):
        self.misses += 1

    @property
    def total(self):
        return self.hits + self.misses

    @property
    def hit_rate(self):
        if self.total == 0:
            return 0
        return (self.hits / self.total) * 100

    def reset(self):
        self.hits = 0
        self.misses = 0

    def get_stats(self):
        return {
            'hits': self.hits,
            'misses': self.misses,
            'total': self.total,
            'hit_rate': f'{self.hit_rate:.2f}%'
        }


# 전역 캐시 추적기
cache_tracker = CachePerformanceTracker()
