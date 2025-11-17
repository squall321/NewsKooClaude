#!/usr/bin/env python3
"""
데모 데이터 시드 스크립트
실제 사용 가능한 샘플 데이터 생성
"""
import os
import sys
from datetime import datetime, timedelta
import random

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import (
    User, Category, Tag, Source, Inspiration,
    WritingStyle, Draft, Post
)


def create_demo_users():
    """데모 사용자 생성"""
    print("👤 사용자 생성 중...")

    users = [
        {
            'username': 'admin',
            'email': 'admin@newskoo.com',
            'password': 'admin123',  # 실제로는 해싱됨
            'role': 'admin',
            'display_name': '관리자'
        },
        {
            'username': 'editor',
            'email': 'editor@newskoo.com',
            'password': 'editor123',
            'role': 'editor',
            'display_name': '에디터'
        }
    ]

    created_users = []
    for user_data in users:
        user = User.query.filter_by(username=user_data['username']).first()
        if not user:
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                role=user_data['role'],
                display_name=user_data['display_name']
            )
            user.set_password(user_data['password'])
            db.session.add(user)
            created_users.append(user)
            print(f"  ✅ {user.username} ({user.role})")
        else:
            created_users.append(user)
            print(f"  ⏭️  {user.username} (이미 존재)")

    db.session.commit()
    return created_users


def create_categories():
    """카테고리 생성"""
    print("\n📂 카테고리 생성 중...")

    categories_data = [
        {'name': 'IT/개발', 'slug': 'it-dev', 'description': '프로그래밍, 개발자 유머'},
        {'name': '의료/건강', 'slug': 'medical', 'description': '병원, 의사, 환자 유머'},
        {'name': '직장생활', 'slug': 'workplace', 'description': '회사, 상사, 동료 유머'},
        {'name': '일상/생활', 'slug': 'daily-life', 'description': '일상적인 재미있는 이야기'},
        {'name': '가족/육아', 'slug': 'family', 'description': '부모, 아이들 이야기'},
        {'name': '학교/교육', 'slug': 'education', 'description': '학생, 선생님 유머'},
    ]

    categories = []
    for cat_data in categories_data:
        cat = Category.query.filter_by(slug=cat_data['slug']).first()
        if not cat:
            cat = Category(**cat_data)
            db.session.add(cat)
            categories.append(cat)
            print(f"  ✅ {cat.name}")
        else:
            categories.append(cat)
            print(f"  ⏭️  {cat.name} (이미 존재)")

    db.session.commit()
    return categories


def create_tags():
    """태그 생성"""
    print("\n🏷️  태그 생성 중...")

    tags_data = [
        'funny', 'wholesome', 'sarcastic', 'dark-humor',
        'relatable', 'nostalgic', 'cute', 'savage',
        'awkward', 'clever', 'weird', 'brilliant'
    ]

    tags = []
    for tag_name in tags_data:
        tag = Tag.query.filter_by(name=tag_name).first()
        if not tag:
            tag = Tag(name=tag_name, slug=tag_name)
            db.session.add(tag)
            tags.append(tag)
            print(f"  ✅ {tag.name}")
        else:
            tags.append(tag)

    db.session.commit()
    return tags


def create_writing_styles(user):
    """작성 스타일 생성"""
    print("\n✍️  작성 스타일 생성 중...")

    styles_data = [
        {
            'name': '친근한 블로그체',
            'tone': '캐주얼하고 친근한 톤',
            'style_guide': '반말 사용, 이모지 적절히 사용, 독자와 대화하듯 작성'
        },
        {
            'name': '전문적인 기사체',
            'tone': '격식 있고 정확한 톤',
            'style_guide': '정확한 표현, 객관적 서술, 이모지 자제'
        },
        {
            'name': '유머러스한 스토리텔링',
            'tone': '재치있고 위트있는 톤',
            'style_guide': '과장된 표현 활용, 비유와 은유 사용, 반전 포인트 강조'
        }
    ]

    styles = []
    for style_data in styles_data:
        style = WritingStyle(user_id=user.id, **style_data)
        db.session.add(style)
        styles.append(style)
        print(f"  ✅ {style.name}")

    db.session.commit()
    return styles


def create_demo_posts(categories, tags, user):
    """데모 게시물 생성"""
    print("\n📝 게시물 생성 중...")

    posts_data = [
        {
            'title': '프로그래머가 바에 들어갔다',
            'slug': 'programmer-walks-into-bar',
            'content': '''# 프로그래머가 바에 들어갔다

프로그래머가 바에 들어가서 말했다:

"맥주 1잔 주세요."

바텐더가 맥주를 주었다.

프로그래머: "맥주 0잔 주세요."

바텐더가 아무것도 주지 않았다.

프로그래머: "맥주 -1잔 주세요."

바텐더가 당황했다.

프로그래머: "맥주 999999999999잔 주세요."

바가 폭발했다. 🍺💥

**교훈:** 항상 입력값을 검증하세요!
''',
            'excerpt': '프로그래머와 바텐더의 대화에서 배우는 입력값 검증의 중요성',
            'category_idx': 0,
            'tag_names': ['funny', 'relatable', 'clever'],
            'views': 1234,
            'published_at': datetime.now() - timedelta(days=5)
        },
        {
            'title': '의사 선생님의 농담',
            'slug': 'doctor-joke',
            'content': '''# 의사 선생님의 농담

환자: "선생님, 제가 투명인간이 된 것 같아요."

의사: "아... 지금은 환자분을 볼 수 없는데요."

---

환자: "선생님, 기억력이 너무 안 좋아요."

의사: "언제부터 그러셨어요?"

환자: "언제부터요?"

---

환자: "선생님, 저 간이 안 좋다고 들었어요."

의사: "어디서 들으셨어요?"

환자: "간에서요." 🏥
''',
            'excerpt': '병원에서 일어나는 재미있는 대화들',
            'category_idx': 1,
            'tag_names': ['funny', 'wholesome'],
            'views': 856,
            'published_at': datetime.now() - timedelta(days=3)
        },
        {
            'title': '회사 미팅 빙고 게임',
            'slug': 'meeting-bingo',
            'content': '''# 회사 미팅 빙고

다음 중 3개 이상 들으면 빙고! 🎯

- "싱크를 맞춰서"
- "일단 해봅시다"
- "고객 관점에서"
- "시너지 효과"
- "win-win"
- "아웃 오브 박스"
- "한 번 더 생각해보죠"
- "일정이 타이트한데"
- "리소스가 부족해서"

**보너스:** "퀵하게" 나오면 자동 빙고! 😂

*당신의 미팅 점수는?*
''',
            'excerpt': '직장인이라면 공감할 회의 필수 멘트들',
            'category_idx': 2,
            'tag_names': ['relatable', 'sarcastic', 'savage'],
            'views': 2103,
            'published_at': datetime.now() - timedelta(days=1)
        },
        {
            'title': '부모님의 IT 지원 요청',
            'slug': 'parents-it-support',
            'content': '''# 부모님의 IT 지원 요청 📱

**오전 10시**
엄마: "아들아, 컴퓨터가 안 켜져"
나: "전원 버튼 누르셨어요?"
엄마: "응"
나: "...전원 코드는 꽂혀있어요?"
엄마: "잠깐만... 아 이거?"

**오후 2시**
아빠: "이거 와이파이가 왜 안 돼?"
나: "비행기 모드 꺼보세요"
아빠: "비행기는 안 타는데?"

**저녁 7시**
엄마: "인터넷이 느려"
나: "라우터 껐다 켜보세요"
엄마: "그게 뭐야?"
나: "...집에 갈게요"

**밤 11시**
아빠: "아들, 급해! 카톡이 안 와!"
나: "전화 소리 켜보세요..."
아빠: "오! 됐다! 천재야!" 🤦‍♂️
''',
            'excerpt': 'IT 직군이라면 누구나 겪는 가족 기술지원',
            'category_idx': 4,
            'tag_names': ['relatable', 'wholesome', 'funny'],
            'views': 1567,
            'published_at': datetime.now() - timedelta(hours=12)
        },
        {
            'title': '선생님의 명언 모음',
            'slug': 'teacher-quotes',
            'content': '''# 선생님들의 명언 📚

### 초등학교
"화장실은 쉬는 시간에!"
*→ 방광: 교육과정 무시*

### 중학교
"너네 반은 내가 가르친 반 중에 최악이야"
*→ 작년, 재작년도 최악이었음*

### 고등학교
"이거 시험에 안 나와"
*→ 100% 나옴*

### 대학교
교수: "출석 안 부릅니다"
*→ 다음 주: "어? 사람이 왜 이렇게 없지?"*

**보너스 레전드**
"야! 너 나랑 눈 마주쳤지? 문제 풀어봐!"
*→ 창밖 새 보고 있었는데...*

🎓 학창시절 공감 100%
''',
            'excerpt': '학생들이라면 누구나 들어본 선생님 멘트',
            'category_idx': 5,
            'tag_names': ['nostalgic', 'relatable', 'funny'],
            'views': 982,
            'published_at': datetime.now() - timedelta(hours=6)
        }
    ]

    created_posts = []
    for post_data in posts_data:
        # Check if post exists
        post = Post.query.filter_by(slug=post_data['slug']).first()
        if post:
            print(f"  ⏭️  {post.title} (이미 존재)")
            continue

        # Create post
        post = Post(
            title=post_data['title'],
            slug=post_data['slug'],
            content=post_data['content'],
            excerpt=post_data['excerpt'],
            user_id=user.id,
            category_id=categories[post_data['category_idx']].id,
            status='published',
            views=post_data['views'],
            published_at=post_data['published_at']
        )

        # Add tags
        for tag_name in post_data['tag_names']:
            tag = next((t for t in tags if t.name == tag_name), None)
            if tag:
                post.tags.append(tag)

        db.session.add(post)
        created_posts.append(post)
        print(f"  ✅ {post.title}")

    db.session.commit()
    return created_posts


def seed_all():
    """모든 데모 데이터 생성"""
    print("=" * 60)
    print("🌱 데모 데이터 시드 시작")
    print("=" * 60)

    app = create_app('development')

    with app.app_context():
        # Create demo data
        users = create_demo_users()
        categories = create_categories()
        tags = create_tags()

        admin_user = users[0]

        writing_styles = create_writing_styles(admin_user)
        posts = create_demo_posts(categories, tags, admin_user)

        print("\n" + "=" * 60)
        print("✅ 데모 데이터 시드 완료!")
        print("=" * 60)
        print(f"\n📊 생성된 데이터:")
        print(f"  - 사용자: {len(users)}명")
        print(f"  - 카테고리: {len(categories)}개")
        print(f"  - 태그: {len(tags)}개")
        print(f"  - 작성 스타일: {len(writing_styles)}개")
        print(f"  - 게시물: {len(posts)}개")

        print(f"\n🔐 로그인 정보:")
        print(f"  관리자: admin@newskoo.com / admin123")
        print(f"  에디터: editor@newskoo.com / editor123")

        print(f"\n🌐 다음 단계:")
        print(f"  1. 백엔드 실행: cd backend && python run.py")
        print(f"  2. 프론트엔드 실행: cd frontend && npm run dev")
        print(f"  3. 브라우저에서 http://localhost:5173 접속")


if __name__ == '__main__':
    seed_all()
