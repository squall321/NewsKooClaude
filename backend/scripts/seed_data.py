"""
Seed 데이터 생성 스크립트
개발 환경을 위한 초기 데이터 생성
"""
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import (
    User, Category, Tag, WritingStyle,
    Source, Inspiration, Draft, Post
)


def create_users():
    """관리자 및 작성자 계정 생성"""
    print("Creating users...")

    users_data = [
        {
            'username': 'admin',
            'email': 'admin@newskoo.com',
            'password': 'admin123',  # 실제 환경에서는 변경 필요
            'role': 'admin',
            'is_active': True
        },
        {
            'username': 'editor1',
            'email': 'editor@newskoo.com',
            'password': 'editor123',
            'role': 'editor',
            'is_active': True
        },
        {
            'username': 'writer1',
            'email': 'writer@newskoo.com',
            'password': 'writer123',
            'role': 'writer',
            'is_active': True
        }
    ]

    created_users = {}
    for user_data in users_data:
        username = user_data['username']
        existing = User.query.filter_by(username=username).first()

        if not existing:
            user = User.create(**user_data)
            db.session.commit()
            created_users[username] = user
            print(f"  ✓ Created user: {username}")
        else:
            created_users[username] = existing
            print(f"  - User already exists: {username}")

    return created_users


def create_categories():
    """카테고리 생성"""
    print("\nCreating categories...")

    categories_data = [
        {'name': '일상 유머', 'description': '일상에서 일어나는 재미있는 이야기'},
        {'name': '풍자', 'description': '사회 현상을 풍자한 유머'},
        {'name': '말장난', 'description': '언어 유희를 이용한 유머'},
        {'name': '블랙 유머', 'description': '블랙 코미디와 어두운 유머'},
        {'name': '상황극', 'description': '상황을 설정한 유머'},
        {'name': '기타', 'description': '기타 유형의 유머'}
    ]

    created_categories = {}
    for cat_data in categories_data:
        name = cat_data['name']
        existing = Category.query.filter_by(name=name).first()

        if not existing:
            category = Category.create(**cat_data)
            db.session.commit()
            created_categories[name] = category
            print(f"  ✓ Created category: {name}")
        else:
            created_categories[name] = existing
            print(f"  - Category already exists: {name}")

    return created_categories


def create_tags():
    """태그 생성"""
    print("\nCreating tags...")

    tags_data = [
        '재미있음', '웃긴', '공감', '현실',
        '직장인', '학생', '연애', '가족',
        '동물', '음식', '여행', '취미',
        '언어유희', '반전', '상황극', '풍자'
    ]

    created_tags = {}
    for tag_name in tags_data:
        existing = Tag.query.filter_by(name=tag_name).first()

        if not existing:
            tag = Tag.create(name=tag_name)
            db.session.commit()
            created_tags[tag_name] = tag
            print(f"  ✓ Created tag: {tag_name}")
        else:
            created_tags[tag_name] = existing
            print(f"  - Tag already exists: {tag_name}")

    return created_tags


def create_writing_styles():
    """작성 스타일/프롬프트 템플릿 생성"""
    print("\nCreating writing styles...")

    styles_data = [
        {
            'name': '캐주얼 유머 스타일',
            'prompt_template': (
                "다음 컨셉을 바탕으로 캐주얼하고 친근한 유머 콘텐츠를 작성해주세요:\n\n"
                "컨셉: {concept}\n\n"
                "요구사항:\n"
                "- 친근하고 편안한 어조\n"
                "- 일상적인 표현 사용\n"
                "- 200-500자 분량\n"
                "- 이모티콘 사용 가능"
            ),
            'system_message': '당신은 유머러스하고 친근한 콘텐츠 작가입니다.',
            'is_active': True
        },
        {
            'name': '풍자 스타일',
            'prompt_template': (
                "다음 주제를 바탕으로 날카로운 풍자 콘텐츠를 작성해주세요:\n\n"
                "주제: {concept}\n\n"
                "요구사항:\n"
                "- 사회 현상에 대한 비판적 시각\n"
                "- 은유와 비유 활용\n"
                "- 300-600자 분량\n"
                "- 품위있는 표현"
            ),
            'system_message': '당신은 사회 현상을 예리하게 관찰하고 풍자하는 작가입니다.',
            'is_active': True
        },
        {
            'name': '스토리텔링 스타일',
            'prompt_template': (
                "다음 아이디어를 바탕으로 이야기 형식의 유머 콘텐츠를 작성해주세요:\n\n"
                "아이디어: {concept}\n\n"
                "요구사항:\n"
                "- 서론-본론-결론 구조\n"
                "- 등장인물과 상황 설정\n"
                "- 500-800자 분량\n"
                "- 마지막에 반전 또는 웃음 포인트"
            ),
            'system_message': '당신은 이야기를 재미있게 풀어내는 스토리텔러입니다.',
            'is_active': True
        }
    ]

    created_styles = {}
    for style_data in styles_data:
        name = style_data['name']
        existing = WritingStyle.query.filter_by(name=name).first()

        if not existing:
            style = WritingStyle.create(**style_data)
            db.session.commit()
            created_styles[name] = style
            print(f"  ✓ Created writing style: {name}")
        else:
            created_styles[name] = existing
            print(f"  - Writing style already exists: {name}")

    return created_styles


def create_sample_content(users, categories, tags, styles):
    """샘플 콘텐츠 생성 (Source, Inspiration, Draft, Post)"""
    print("\nCreating sample content...")

    # Sample Source
    source = Source.create(
        platform='reddit',
        source_url='https://reddit.com/r/funny/example',
        source_id='example123',
        title='Funny cat behavior',
        author='reddit_user',
        score=1500,
        metadata_json='{"subreddit": "funny", "num_comments": 234}'
    )
    db.session.commit()
    print("  ✓ Created sample source")

    # Sample Inspiration
    inspiration = Inspiration.create(
        source_id=source.id,
        original_concept='고양이가 이상한 행동을 하는 상황',
        adaptation_notes='한국 문화에 맞게 반려묘 관점으로 재창작',
        similarity_score=0.35,  # 35% (Fair Use 준수)
        status='approved'
    )
    db.session.commit()
    print("  ✓ Created sample inspiration")

    # Sample Draft
    draft = Draft.create(
        user_id=users['writer1'].id,
        inspiration_id=inspiration.id,
        writing_style_id=styles['캐주얼 유머 스타일'].id,
        title='우리집 고양이는 사실 외계인이 아닐까',
        content=(
            "오늘도 우리집 고양이를 관찰했다.\n\n"
            "새벽 3시에 아무 이유 없이 집안을 전력질주하고,\n"
            "창밖을 보며 아무것도 없는 허공에 대고 야옹거린다.\n\n"
            "심지어 화장실 문을 스스로 열 수 있다는 걸 오늘 알았다.\n"
            "문고리를 앞발로 당기더니 스윽 들어가더라...\n\n"
            "이건 고양이가 아니라 외계 생명체가 아닐까 의심된다."
        ),
        status='completed'
    )
    db.session.commit()
    print("  ✓ Created sample draft")

    # Sample Post (from draft)
    post = Post.create(
        user_id=users['writer1'].id,
        category_id=categories['일상 유머'].id,
        draft_id=draft.id,
        title=draft.title,
        content=draft.content,
        thumbnail_url=None,
        is_published=True
    )

    # Set tags
    post.set_tags(['재미있음', '공감', '동물'])

    # Publish
    post.publish()

    print("  ✓ Created and published sample post")

    return {
        'source': source,
        'inspiration': inspiration,
        'draft': draft,
        'post': post
    }


def main():
    """메인 실행 함수"""
    print("=" * 50)
    print("NewsKoo Seed Data Generator")
    print("=" * 50)

    # Flask 앱 생성
    app = create_app('development')

    with app.app_context():
        # 데이터베이스 생성 (없을 경우)
        print("\nInitializing database...")
        db.create_all()
        print("  ✓ Database initialized")

        # Seed 데이터 생성
        users = create_users()
        categories = create_categories()
        tags = create_tags()
        styles = create_writing_styles()
        sample_content = create_sample_content(users, categories, tags, styles)

        print("\n" + "=" * 50)
        print("Seed data creation completed!")
        print("=" * 50)
        print(f"\nCreated:")
        print(f"  - {len(users)} users")
        print(f"  - {len(categories)} categories")
        print(f"  - {len(tags)} tags")
        print(f"  - {len(styles)} writing styles")
        print(f"  - 1 sample source")
        print(f"  - 1 sample inspiration")
        print(f"  - 1 sample draft")
        print(f"  - 1 sample post")
        print("\nDefault login:")
        print("  Username: admin")
        print("  Password: admin123")
        print("  (Change this in production!)")
        print("\n" + "=" * 50)


if __name__ == '__main__':
    main()
