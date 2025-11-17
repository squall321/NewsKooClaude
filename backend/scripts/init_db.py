#!/usr/bin/env python3
"""
데이터베이스 초기화 스크립트
마이그레이션 생성 및 테이블 초기화
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from flask_migrate import init, migrate, upgrade


def init_database():
    """데이터베이스 초기화"""
    print("🚀 데이터베이스 초기화 시작...")

    app = create_app('development')

    with app.app_context():
        # Check if migrations directory exists
        migrations_dir = os.path.join(os.path.dirname(__file__), '..', 'migrations')

        if not os.path.exists(migrations_dir):
            print("📁 마이그레이션 디렉토리 생성 중...")
            init()
            print("✅ 마이그레이션 디렉토리 생성 완료")
        else:
            print("✅ 마이그레이션 디렉토리 이미 존재")

        # Import all models to ensure they're registered
        print("📦 모델 로딩 중...")
        from app.models import (
            User, Category, Tag, Source, Inspiration,
            WritingStyle, Draft, Post
        )
        print("✅ 모델 로딩 완료")

        # Create migration
        print("🔄 마이그레이션 생성 중...")
        try:
            migrate(message="Initial migration")
            print("✅ 마이그레이션 생성 완료")
        except Exception as e:
            print(f"⚠️  마이그레이션 생성 중 오류 (이미 존재할 수 있음): {e}")

        # Apply migrations
        print("⬆️  마이그레이션 적용 중...")
        try:
            upgrade()
            print("✅ 마이그레이션 적용 완료")
        except Exception as e:
            print(f"❌ 마이그레이션 적용 실패: {e}")
            # Try creating tables directly
            print("🔧 테이블 직접 생성 시도...")
            db.create_all()
            print("✅ 테이블 생성 완료")

        # Verify tables
        print("\n📊 생성된 테이블 확인:")
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        for table in sorted(tables):
            print(f"  - {table}")

        print(f"\n✅ 총 {len(tables)}개 테이블 생성됨")
        print("\n🎉 데이터베이스 초기화 완료!")


def reset_database():
    """데이터베이스 완전 초기화 (모든 데이터 삭제)"""
    print("⚠️  WARNING: 모든 데이터가 삭제됩니다!")
    confirm = input("계속하시겠습니까? (yes/no): ")

    if confirm.lower() != 'yes':
        print("❌ 취소되었습니다.")
        return

    app = create_app('development')

    with app.app_context():
        print("🗑️  기존 테이블 삭제 중...")
        db.drop_all()
        print("✅ 테이블 삭제 완료")

        print("🔧 테이블 재생성 중...")
        db.create_all()
        print("✅ 테이블 재생성 완료")

        print("\n🎉 데이터베이스 리셋 완료!")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='데이터베이스 초기화 도구')
    parser.add_argument(
        '--reset',
        action='store_true',
        help='데이터베이스 완전 초기화 (모든 데이터 삭제)'
    )

    args = parser.parse_args()

    if args.reset:
        reset_database()
    else:
        init_database()
