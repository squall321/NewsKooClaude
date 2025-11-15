#!/usr/bin/env python3
"""
Draft API 테스트 스크립트

Draft CRUD, 이미지 업로드, 자동 저장, 발행 기능을 테스트합니다.
"""
import os
import sys
import io
from pathlib import Path
from PIL import Image

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import create_app, db
from app.models import User, Category, WritingStyle, Draft, Post
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()


def create_test_image():
    """테스트용 이미지 생성"""
    img = Image.new('RGB', (800, 600), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes


def setup_test_data(app):
    """테스트 데이터 생성"""
    print("=== Setting up test data ===\n")

    with app.app_context():
        # 기존 테스트 데이터 삭제
        Draft.query.filter_by(title='Test Draft').delete()
        Post.query.filter_by(title='Test Draft').delete()
        User.query.filter_by(username='draft_tester').delete()
        Category.query.filter_by(name='Test Category').delete()
        WritingStyle.query.filter_by(name='Test Style').delete()

        # 사용자 생성
        user = User.create(
            username='draft_tester',
            email='draft_tester@example.com',
            password='test1234',
            role='editor'
        )
        user_id = user.id

        # 카테고리 생성
        category = Category.create(
            name='Test Category',
            slug='test-category',
            description='Test category for drafts'
        )
        category_id = category.id

        # 작성 스타일 생성
        style = WritingStyle.create(
            user_id=user_id,
            name='Test Style',
            description='Test writing style',
            tone='humorous',
            style_guide='Be funny and engaging'
        )
        style_id = style.id

        db.session.commit()

        print(f"✓ Test user created: {user.username} (ID: {user_id})")
        print(f"✓ Test category created: {category.name} (ID: {category_id})")
        print(f"✓ Test style created: {style.name} (ID: {style_id})")
        print()

        return user_id, category_id, style_id


def test_draft_creation(app, user_id, category_id, style_id):
    """Draft 생성 테스트"""
    print("=" * 80)
    print("TEST 1: Draft Creation")
    print("=" * 80)
    print()

    with app.app_context():
        # Draft 생성
        draft = Draft.create(
            user_id=user_id,
            category_id=category_id,
            title='Test Draft',
            content='# Test Content\n\nThis is a test draft with **markdown**.',
            writing_style_id=style_id,
            ai_generated=False
        )
        draft_id = draft.id

        db.session.commit()

        print(f"✓ Draft created: {draft.title} (ID: {draft_id})")
        print(f"  Category: {draft.category.name}")
        print(f"  Writing Style: {draft.writing_style.name if draft.writing_style else 'None'}")
        print(f"  AI Generated: {draft.ai_generated}")
        print(f"  Created at: {draft.created_at}")
        print()

        return draft_id


def test_draft_list(app, user_id):
    """Draft 목록 조회 테스트"""
    print("=" * 80)
    print("TEST 2: Draft List")
    print("=" * 80)
    print()

    with app.app_context():
        # 사용자의 모든 Draft 조회
        drafts = Draft.query.filter_by(user_id=user_id).all()

        print(f"Total drafts for user {user_id}: {len(drafts)}")
        for draft in drafts:
            print(f"  - {draft.title} (ID: {draft.id})")
            print(f"    Status: {'Published' if draft.post_id else 'Draft'}")
            print(f"    Updated: {draft.updated_at}")
        print()


def test_draft_update(app, draft_id):
    """Draft 수정 테스트"""
    print("=" * 80)
    print("TEST 3: Draft Update")
    print("=" * 80)
    print()

    with app.app_context():
        draft = Draft.query.get(draft_id)

        # 제목 및 내용 수정
        original_title = draft.title
        draft.title = 'Updated Test Draft'
        draft.content = '# Updated Content\n\nThis content has been **updated**.'

        db.session.commit()

        print(f"✓ Draft updated")
        print(f"  Original title: {original_title}")
        print(f"  New title: {draft.title}")
        print(f"  Updated at: {draft.updated_at}")
        print()


def test_autosave(app, draft_id):
    """자동 저장 테스트"""
    print("=" * 80)
    print("TEST 4: Autosave")
    print("=" * 80)
    print()

    with app.app_context():
        draft = Draft.query.get(draft_id)

        # 자동 저장 (검증 없이 즉시 저장)
        draft.content = '# Autosaved Content\n\nThis was saved automatically.'

        db.session.commit()

        print(f"✓ Draft autosaved")
        print(f"  Draft ID: {draft_id}")
        print(f"  Saved at: {draft.updated_at.isoformat()}")
        print()


def test_image_upload(app, draft_id):
    """이미지 업로드 테스트"""
    print("=" * 80)
    print("TEST 5: Image Upload")
    print("=" * 80)
    print()

    with app.app_context():
        from app.services.image_processor import ImageProcessor

        # 이미지 프로세서 초기화
        upload_folder = Path(app.config.get('UPLOAD_FOLDER', 'uploads'))
        processor = ImageProcessor(upload_folder)

        # 테스트 이미지 생성
        print("Creating test image...")
        test_image = create_test_image()

        # Mock FileStorage
        from werkzeug.datastructures import FileStorage
        file = FileStorage(
            stream=test_image,
            filename='test_image.jpg',
            content_type='image/jpeg'
        )

        try:
            # 이미지 업로드
            result = processor.upload_image(file, create_thumbnail=True)

            print(f"✓ Image uploaded successfully")
            print(f"  Filename: {result['filename']}")
            print(f"  Original filename: {result['original_filename']}")
            print(f"  URL: {result['url']}")
            print(f"  Thumbnail URL: {result['thumbnail_url']}")
            print(f"  Size: {result['width']}x{result['height']} ({result['size']} bytes)")
            print()

            return result['filename']

        except Exception as e:
            print(f"✗ Image upload failed: {e}")
            print()
            return None


def test_image_deletion(app, filename):
    """이미지 삭제 테스트"""
    print("=" * 80)
    print("TEST 6: Image Deletion")
    print("=" * 80)
    print()

    if not filename:
        print("⚠ Skipping - no image to delete")
        print()
        return

    with app.app_context():
        from app.services.image_processor import ImageProcessor

        upload_folder = Path(app.config.get('UPLOAD_FOLDER', 'uploads'))
        processor = ImageProcessor(upload_folder)

        try:
            # 이미지 삭제
            processor.delete_image(filename, delete_thumbnail=True)

            print(f"✓ Image deleted successfully")
            print(f"  Filename: {filename}")
            print()

        except Exception as e:
            print(f"✗ Image deletion failed: {e}")
            print()


def test_draft_publish(app, draft_id):
    """Draft 발행 테스트"""
    print("=" * 80)
    print("TEST 7: Draft Publish")
    print("=" * 80)
    print()

    with app.app_context():
        draft = Draft.query.get(draft_id)

        # Post 생성
        post = Post.create(
            user_id=draft.user_id,
            category_id=draft.category_id,
            title=draft.title,
            content=draft.content
        )

        # 발행
        post.publish()

        # Draft와 Post 연결
        draft.post_id = post.id

        db.session.commit()

        print(f"✓ Draft published successfully")
        print(f"  Draft ID: {draft_id}")
        print(f"  Post ID: {post.id}")
        print(f"  Post title: {post.title}")
        print(f"  Post status: {post.status}")
        print(f"  Published at: {post.published_at}")
        print()

        return post.id


def test_draft_deletion(app):
    """Draft 삭제 테스트"""
    print("=" * 80)
    print("TEST 8: Draft Deletion")
    print("=" * 80)
    print()

    with app.app_context():
        # 새 Draft 생성 (삭제 테스트용)
        user = User.query.filter_by(username='draft_tester').first()
        category = Category.query.filter_by(name='Test Category').first()

        draft = Draft.create(
            user_id=user.id,
            category_id=category.id,
            title='Draft to Delete',
            content='This draft will be deleted.',
            ai_generated=False
        )
        draft_id = draft.id

        db.session.commit()

        print(f"✓ Draft created for deletion: ID {draft_id}")

        # Draft 삭제
        db.session.delete(draft)
        db.session.commit()

        print(f"✓ Draft deleted successfully")
        print()


def cleanup_test_data(app):
    """테스트 데이터 정리"""
    print("=" * 80)
    print("Cleaning up test data")
    print("=" * 80)
    print()

    with app.app_context():
        # 테스트 데이터 삭제
        Draft.query.filter_by(title='Updated Test Draft').delete()
        Post.query.filter_by(title='Updated Test Draft').delete()
        User.query.filter_by(username='draft_tester').delete()
        Category.query.filter_by(name='Test Category').delete()
        WritingStyle.query.filter_by(name='Test Style').delete()

        db.session.commit()

        print("✓ Test data cleaned up")
        print()


def main():
    """메인 실행 함수"""
    print("\n")
    print("=" * 80)
    print("Draft API Test Suite")
    print("=" * 80)
    print("\n")

    app = create_app('development')

    try:
        # 테스트 데이터 생성
        user_id, category_id, style_id = setup_test_data(app)
        input("Press Enter to continue to draft creation test...")
        print("\n")

        # 1. Draft 생성 테스트
        draft_id = test_draft_creation(app, user_id, category_id, style_id)
        input("Press Enter to continue to draft list test...")
        print("\n")

        # 2. Draft 목록 조회 테스트
        test_draft_list(app, user_id)
        input("Press Enter to continue to draft update test...")
        print("\n")

        # 3. Draft 수정 테스트
        test_draft_update(app, draft_id)
        input("Press Enter to continue to autosave test...")
        print("\n")

        # 4. 자동 저장 테스트
        test_autosave(app, draft_id)
        input("Press Enter to continue to image upload test...")
        print("\n")

        # 5. 이미지 업로드 테스트
        uploaded_filename = test_image_upload(app, draft_id)
        input("Press Enter to continue to image deletion test...")
        print("\n")

        # 6. 이미지 삭제 테스트
        test_image_deletion(app, uploaded_filename)
        input("Press Enter to continue to draft publish test...")
        print("\n")

        # 7. Draft 발행 테스트
        post_id = test_draft_publish(app, draft_id)
        input("Press Enter to continue to draft deletion test...")
        print("\n")

        # 8. Draft 삭제 테스트
        test_draft_deletion(app)
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
