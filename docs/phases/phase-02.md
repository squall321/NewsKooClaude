# Phase 2: 데이터베이스 설계 및 모델 정의

**난이도**: ⭐⭐⭐☆☆
**예상 소요 시간**: 3-4시간
**우선순위**: P0 (필수)

## 목표

데이터베이스 스키마를 설계하고, SQLAlchemy 모델을 정의하여 데이터 구조의 기반을 마련합니다. "번역"이 아닌 "재창작" 철학을 반영한 데이터 구조를 만듭니다.

## 선행 요구사항

- Phase 1 완료 (Flask 프로젝트 구조 생성)
- SQLAlchemy, Flask-Migrate 설치 완료
- 데이터베이스 기본 개념 이해

---

## ERD (Entity Relationship Diagram)

```
┌─────────────────┐         ┌──────────────────┐
│  User           │         │  Category        │
├─────────────────┤         ├──────────────────┤
│ id (PK)         │         │ id (PK)          │
│ username        │         │ name             │
│ email           │         │ slug             │
│ password_hash   │         │ icon             │
│ role            │         │ color            │
│ created_at      │         │ description      │
└─────────────────┘         └──────────────────┘
        │                            │
        │                            │
        │ 1:N                        │ 1:N
        │                            │
        ▼                            ▼
┌──────────────────────────────────────────────┐
│  Post (재구성된 게시물 - 독립적 창작물)       │
├──────────────────────────────────────────────┤
│ id (PK)                                      │
│ title                                        │
│ content (마크다운)                           │
│ excerpt                                      │
│ thumbnail                                    │
│ author_id (FK → User)                        │
│ category_id (FK → Category)                  │
│ view_count                                   │
│ published                                    │
│ original_inspiration_id (FK, nullable)       │
│ created_at                                   │
│ updated_at                                   │
│ published_at                                 │
└──────────────────────────────────────────────┘
        │                            │
        │ N:M (through post_tags)    │
        ▼                            ▼
┌─────────────────┐         ┌──────────────────┐
│  Tag            │         │  Draft           │
├─────────────────┤         ├──────────────────┤
│ id (PK)         │         │ id (PK)          │
│ name            │         │ title            │
└─────────────────┘         │ content          │
                            │ status           │
                            │ author_id (FK)   │
                            │ inspiration_id   │
                            │ ai_versions (JSON)│
                            │ created_at       │
                            │ updated_at       │
                            └──────────────────┘
                                     │
                                     │ N:1
                                     ▼
                            ┌──────────────────────────┐
                            │  SourceInspiration       │
                            │  (원본 메타데이터만)      │
                            ├──────────────────────────┤
                            │ id (PK)                  │
                            │ title                    │
                            │ url                      │
                            │ source (reddit/twitter)  │
                            │ subreddit                │
                            │ upvotes                  │
                            │ comments_count           │
                            │ created_at               │
                            │ collected_at             │
                            │ bookmarked               │
                            │ hidden                   │
                            └──────────────────────────┘

┌─────────────────────────────────────────────┐
│  WritingStyle (블로그 스타일 가이드)         │
├─────────────────────────────────────────────┤
│ id (PK)                                     │
│ name                                        │
│ tone (casual/formal/humorous)               │
│ preferred_phrases (JSON)                    │
│ forbidden_words (JSON)                      │
│ sentence_length_preference                  │
│ example_posts (JSON - Few-shot learning)    │
│ is_active                                   │
└─────────────────────────────────────────────┘
```

---

## 구현 단계

### 1단계: Base 모델 생성

**backend/app/models/__init__.py**:
```python
from datetime import datetime
from app import db

class TimestampMixin:
    """생성/수정 시간 자동 관리"""
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class BaseModel(db.Model, TimestampMixin):
    """모든 모델의 베이스 클래스"""
    __abstract__ = True

    def to_dict(self):
        """모델을 딕셔너리로 변환"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

    def save(self):
        """저장"""
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        """삭제"""
        db.session.delete(self)
        db.session.commit()
```

---

### 2단계: User 모델

**backend/app/models/user.py**:
```python
from app.models import db, BaseModel
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token


class User(BaseModel):
    """사용자 (관리자/작성자)"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='writer', nullable=False)  # admin, writer

    # Relationships
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    drafts = db.relationship('Draft', backref='author', lazy='dynamic')

    def set_password(self, password):
        """비밀번호 해시화"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """비밀번호 확인"""
        return check_password_hash(self.password_hash, password)

    def generate_token(self):
        """JWT 토큰 생성"""
        return create_access_token(identity=self.id)

    def to_dict(self, include_email=False):
        """딕셔너리 변환 (비밀번호 제외)"""
        data = {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'created_at': self.created_at.isoformat()
        }
        if include_email:
            data['email'] = self.email
        return data

    def __repr__(self):
        return f'<User {self.username}>'
```

---

### 3단계: Category & Tag 모델

**backend/app/models/category.py**:
```python
from app.models import db, BaseModel
from slugify import slugify


class Category(BaseModel):
    """카테고리 (IT/개발, 의료, 직장 등)"""
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)
    icon = db.Column(db.String(50))  # lucide-react 아이콘 이름
    color = db.Column(db.String(7), default='#3B82F6')  # HEX 색상
    description = db.Column(db.Text)

    # Relationships
    posts = db.relationship('Post', backref='category', lazy='dynamic')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.slug:
            self.slug = slugify(self.name)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'icon': self.icon,
            'color': self.color,
            'description': self.description,
            'post_count': self.posts.filter_by(published=True).count()
        }

    def __repr__(self):
        return f'<Category {self.name}>'


# Many-to-Many 관계 테이블
post_tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=db.func.now())
)


class Tag(BaseModel):
    """태그"""
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)

    # Relationships (through post_tags)
    posts = db.relationship('Post', secondary=post_tags, backref='tags', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'post_count': self.posts.filter_by(published=True).count()
        }

    def __repr__(self):
        return f'<Tag {self.name}>'
```

**slugify 설치**:
```bash
pip install python-slugify
pip freeze > requirements.txt
```

---

### 4단계: Post 모델 (핵심)

**backend/app/models/post.py**:
```python
from app.models import db, BaseModel
from datetime import datetime


class Post(BaseModel):
    """재구성된 게시물 (원본과 독립적인 창작물)"""
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)

    # 기본 정보
    title = db.Column(db.String(200), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)  # 마크다운
    excerpt = db.Column(db.String(300))  # 요약 (자동 생성 or 수동)

    # 이미지
    thumbnail = db.Column(db.String(255))  # 썸네일 경로

    # 메타데이터
    view_count = db.Column(db.Integer, default=0, index=True)
    published = db.Column(db.Boolean, default=False, index=True)
    published_at = db.Column(db.DateTime, nullable=True)

    # Foreign Keys
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)

    # 영감 소스 (선택적)
    original_inspiration_id = db.Column(
        db.Integer,
        db.ForeignKey('source_inspirations.id'),
        nullable=True
    )

    # SEO
    meta_description = db.Column(db.String(160))
    meta_keywords = db.Column(db.String(255))

    # Relationships
    # tags: backref from Tag model
    # author: backref from User model
    # category: backref from Category model
    inspiration = db.relationship(
        'SourceInspiration',
        backref='adapted_posts',
        foreign_keys=[original_inspiration_id]
    )

    def publish(self):
        """게시물 발행"""
        self.published = True
        self.published_at = datetime.utcnow()
        self.save()

    def unpublish(self):
        """게시물 비공개"""
        self.published = False
        self.save()

    def increment_view(self):
        """조회수 증가"""
        self.view_count += 1
        db.session.commit()

    def to_dict(self, include_content=False):
        """딕셔너리 변환"""
        data = {
            'id': self.id,
            'title': self.title,
            'excerpt': self.excerpt,
            'thumbnail': self.thumbnail,
            'author': self.author.to_dict(),
            'category': self.category.to_dict(),
            'tags': [tag.to_dict() for tag in self.tags],
            'view_count': self.view_count,
            'published': self.published,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

        if include_content:
            data['content'] = self.content

        if self.published_at:
            data['published_at'] = self.published_at.isoformat()

        if self.inspiration:
            data['original_source'] = {
                'url': self.inspiration.url,
                'title': self.inspiration.title
            }

        return data

    def __repr__(self):
        return f'<Post {self.title}>'
```

---

### 5단계: SourceInspiration 모델

**backend/app/models/inspiration.py**:
```python
from app.models import db, BaseModel


class SourceInspiration(BaseModel):
    """영감 소스 (원본 본문 저장 안 함, 메타데이터만)"""
    __tablename__ = 'source_inspirations'

    id = db.Column(db.Integer, primary_key=True)

    # 메타데이터
    title = db.Column(db.String(300), nullable=False)
    url = db.Column(db.String(500), unique=True, nullable=False, index=True)
    source = db.Column(db.String(50), nullable=False)  # reddit, twitter, other

    # Reddit 전용
    subreddit = db.Column(db.String(100))
    upvotes = db.Column(db.Integer, default=0)
    comments_count = db.Column(db.Integer, default=0)

    # 수집 시간 (원본 작성 시간과 구분)
    collected_at = db.Column(db.DateTime, nullable=False)

    # 상태
    bookmarked = db.Column(db.Boolean, default=False, index=True)
    hidden = db.Column(db.Boolean, default=False, index=True)

    # Relationships
    # adapted_posts: backref from Post model

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'url': self.url,
            'source': self.source,
            'subreddit': self.subreddit,
            'upvotes': self.upvotes,
            'comments_count': self.comments_count,
            'collected_at': self.collected_at.isoformat(),
            'bookmarked': self.bookmarked,
            'hidden': self.hidden,
            'adapted_count': len(self.adapted_posts)
        }

    def __repr__(self):
        return f'<SourceInspiration {self.title[:30]}>'
```

---

### 6단계: Draft 모델

**backend/app/models/draft.py**:
```python
from app.models import db, BaseModel
from sqlalchemy.dialects.postgresql import JSON


class Draft(BaseModel):
    """초안 (AI 제안 + 수동 편집)"""
    __tablename__ = 'drafts'

    id = db.Column(db.Integer, primary_key=True)

    # 기본 정보
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)  # 현재 작성 중인 내용

    # 상태
    status = db.Column(
        db.String(20),
        default='writing',
        nullable=False,
        index=True
    )  # writing, ai_pending, review

    # Foreign Keys
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    inspiration_id = db.Column(
        db.Integer,
        db.ForeignKey('source_inspirations.id'),
        nullable=True
    )

    # AI 생성 버전들 (JSON)
    ai_versions = db.Column(JSON, default=list)
    # 예: [
    #   {
    #     "version": 1,
    #     "text": "...",
    #     "style": "casual",
    #     "similarity": 0.65,
    #     "created_at": "2025-01-01T00:00:00"
    #   }
    # ]

    # 메타데이터
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    thumbnail = db.Column(db.String(255))

    # Relationships
    inspiration = db.relationship('SourceInspiration', backref='drafts')
    category = db.relationship('Category')

    def add_ai_version(self, text, style, similarity):
        """AI 재구성 버전 추가"""
        from datetime import datetime

        if self.ai_versions is None:
            self.ai_versions = []

        version = {
            'version': len(self.ai_versions) + 1,
            'text': text,
            'style': style,
            'similarity': similarity,
            'created_at': datetime.utcnow().isoformat()
        }

        self.ai_versions.append(version)
        self.status = 'review'
        self.save()

    def to_post(self):
        """초안을 게시물로 변환"""
        from app.models.post import Post

        post = Post(
            title=self.title,
            content=self.content,
            thumbnail=self.thumbnail,
            author_id=self.author_id,
            category_id=self.category_id,
            original_inspiration_id=self.inspiration_id
        )

        return post

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'status': self.status,
            'author': self.author.to_dict(),
            'inspiration': self.inspiration.to_dict() if self.inspiration else None,
            'category': self.category.to_dict() if self.category else None,
            'ai_versions': self.ai_versions or [],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f'<Draft {self.title}>'
```

---

### 7단계: WritingStyle 모델

**backend/app/models/writing_style.py**:
```python
from app.models import db, BaseModel
from sqlalchemy.dialects.postgresql import JSON


class WritingStyle(BaseModel):
    """블로그 스타일 가이드 (AI 프롬프트용)"""
    __tablename__ = 'writing_styles'

    id = db.Column(db.Integer, primary_key=True)

    # 기본 정보
    name = db.Column(db.String(100), unique=True, nullable=False)
    tone = db.Column(db.String(50), default='casual')  # casual, formal, humorous

    # 스타일 가이드 (JSON)
    preferred_phrases = db.Column(JSON, default=list)
    # 예: ["ㅋㅋㅋ", "ㅎㅎ", "그래서 말인데"]

    forbidden_words = db.Column(JSON, default=list)
    # 예: ["욕설", "비속어"]

    sentence_length_preference = db.Column(db.String(20), default='medium')
    # short, medium, long

    # Few-shot learning 예시 (JSON)
    example_posts = db.Column(JSON, default=list)
    # 예: [
    #   {
    #     "title": "...",
    #     "content": "...",
    #     "notes": "좋은 예시"
    #   }
    # ]

    # 상태
    is_active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'tone': self.tone,
            'preferred_phrases': self.preferred_phrases or [],
            'forbidden_words': self.forbidden_words or [],
            'sentence_length_preference': self.sentence_length_preference,
            'example_posts': self.example_posts or [],
            'is_active': self.is_active
        }

    def to_prompt_context(self):
        """AI 프롬프트에 삽입할 컨텍스트 생성"""
        context = f"작성 스타일: {self.name}\n"
        context += f"톤: {self.tone}\n"

        if self.preferred_phrases:
            context += f"자주 사용하는 표현: {', '.join(self.preferred_phrases[:5])}\n"

        if self.forbidden_words:
            context += f"사용 금지 단어: {', '.join(self.forbidden_words)}\n"

        context += f"문장 길이 선호: {self.sentence_length_preference}\n"

        return context

    def __repr__(self):
        return f'<WritingStyle {self.name}>'
```

---

### 8단계: 모델 통합

**backend/app/models/__init__.py** 업데이트:
```python
from datetime import datetime
from app import db

# Base classes
class TimestampMixin:
    """생성/수정 시간 자동 관리"""
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class BaseModel(db.Model, TimestampMixin):
    """모든 모델의 베이스 클래스"""
    __abstract__ = True

    def to_dict(self):
        """모델을 딕셔너리로 변환"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

    def save(self):
        """저장"""
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        """삭제"""
        db.session.delete(self)
        db.session.commit()


# Import models
from app.models.user import User
from app.models.category import Category, Tag, post_tags
from app.models.post import Post
from app.models.inspiration import SourceInspiration
from app.models.draft import Draft
from app.models.writing_style import WritingStyle

# Export for easy import
__all__ = [
    'db',
    'User',
    'Category',
    'Tag',
    'Post',
    'SourceInspiration',
    'Draft',
    'WritingStyle',
    'post_tags'
]
```

---

### 9단계: 데이터베이스 마이그레이션

#### 9-1. 마이그레이션 초기화

```bash
cd backend
source venv/bin/activate

# Flask-Migrate 초기화
flask db init
```

**예상 출력**:
```
Creating directory /backend/migrations ... done
Creating directory /backend/migrations/versions ... done
Generating /backend/migrations/script.py.mako ... done
```

#### 9-2. 마이그레이션 생성

```bash
flask db migrate -m "Initial schema: users, posts, categories, tags, inspirations, drafts"
```

**예상 출력**:
```
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.autogenerate.compare] Detected added table 'users'
INFO  [alembic.autogenerate.compare] Detected added table 'categories'
...
Generating /backend/migrations/versions/xxx_initial_schema.py ... done
```

#### 9-3. 마이그레이션 적용

```bash
flask db upgrade
```

**예상 출력**:
```
INFO  [alembic.runtime.migration] Running upgrade -> xxx, Initial schema
```

#### 9-4. 데이터베이스 확인

```bash
# SQLite 사용 시
sqlite3 humorhub.db

# 테이블 확인
.tables
```

**예상 출력**:
```
alembic_version       drafts                post_tags             users
categories            posts                 source_inspirations   writing_styles
tags
```

---

### 10단계: 초기 데이터 시드

**backend/scripts/seed_data.py**:
```python
"""초기 데이터 시드"""
from app import create_app, db
from app.models import User, Category, Tag, WritingStyle
from datetime import datetime

app = create_app()

def seed_categories():
    """카테고리 초기 데이터"""
    categories = [
        {
            'name': 'IT/개발',
            'slug': 'it-dev',
            'icon': 'Code',
            'color': '#3B82F6',
            'description': '프로그래머와 개발자의 유머'
        },
        {
            'name': '직장',
            'slug': 'workplace',
            'icon': 'Briefcase',
            'color': '#8B5CF6',
            'description': '회사 생활 관련 유머'
        },
        {
            'name': '의료',
            'slug': 'medical',
            'icon': 'HeartPulse',
            'color': '#EF4444',
            'description': '의사, 간호사 등 의료계 유머'
        },
        {
            'name': '일상',
            'slug': 'daily',
            'icon': 'Home',
            'color': '#10B981',
            'description': '일상 생활 유머'
        },
        {
            'name': '교육',
            'slug': 'education',
            'icon': 'GraduationCap',
            'color': '#F59E0B',
            'description': '학교, 교육 관련 유머'
        }
    ]

    for cat_data in categories:
        if not Category.query.filter_by(slug=cat_data['slug']).first():
            category = Category(**cat_data)
            category.save()
            print(f"✓ Created category: {cat_data['name']}")


def seed_tags():
    """태그 초기 데이터"""
    tags = [
        '버그', '디버깅', '코드리뷰', '퇴근', '야근',
        '상사', '회의', '프로젝트', '고객', '병원',
        '의사', '간호사', '환자', '학교', '선생님'
    ]

    for tag_name in tags:
        if not Tag.query.filter_by(name=tag_name).first():
            tag = Tag(name=tag_name)
            tag.save()
            print(f"✓ Created tag: {tag_name}")


def seed_admin_user():
    """관리자 계정 생성"""
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            email='admin@humorhub.com',
            role='admin'
        )
        admin.set_password('admin123')  # 프로덕션에서는 변경 필수!
        admin.save()
        print(f"✓ Created admin user (username: admin, password: admin123)")


def seed_writing_style():
    """기본 작성 스타일"""
    if not WritingStyle.query.filter_by(name='기본 캐주얼').first():
        style = WritingStyle(
            name='기본 캐주얼',
            tone='casual',
            preferred_phrases=['ㅋㅋㅋ', 'ㅎㅎ', '그래서 말인데', '근데'],
            forbidden_words=['욕설', '비속어'],
            sentence_length_preference='medium',
            is_active=True
        )
        style.save()
        print(f"✓ Created writing style: 기본 캐주얼")


if __name__ == '__main__':
    with app.app_context():
        print("🌱 Seeding database...")
        seed_categories()
        seed_tags()
        seed_admin_user()
        seed_writing_style()
        print("✅ Database seeding complete!")
```

**실행**:
```bash
python scripts/seed_data.py
```

---

## 완료 체크리스트

- [ ] ERD 설계 완료
- [ ] BaseModel, TimestampMixin 생성
- [ ] User 모델 구현 (비밀번호 해싱, JWT)
- [ ] Category, Tag 모델 구현 (N:M 관계)
- [ ] Post 모델 구현 (핵심)
- [ ] SourceInspiration 모델 구현 (메타데이터만)
- [ ] Draft 모델 구현 (AI 버전 JSON)
- [ ] WritingStyle 모델 구현
- [ ] 모든 모델 통합 (models/__init__.py)
- [ ] Flask-Migrate 초기화 (flask db init)
- [ ] 마이그레이션 생성 (flask db migrate)
- [ ] 마이그레이션 적용 (flask db upgrade)
- [ ] 데이터베이스 테이블 생성 확인
- [ ] 초기 데이터 시드 스크립트 작성
- [ ] 시드 실행 (카테고리, 태그, 관리자, 스타일)
- [ ] PROGRESS.md에 Phase 2 완료 기록

---

## 테스트

### 모델 테스트 스크립트

**backend/tests/test_models.py**:
```python
import pytest
from app import create_app, db
from app.models import User, Category, Post, Tag

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_user_model(app):
    """User 모델 테스트"""
    with app.app_context():
        user = User(username='test', email='test@test.com', role='writer')
        user.set_password('password123')
        user.save()

        assert user.id is not None
        assert user.check_password('password123')
        assert not user.check_password('wrong')

def test_post_model(app):
    """Post 모델 테스트"""
    with app.app_context():
        # User 생성
        user = User(username='author', email='author@test.com')
        user.set_password('pass')
        user.save()

        # Category 생성
        category = Category(name='테스트', slug='test', icon='Code')
        category.save()

        # Post 생성
        post = Post(
            title='테스트 게시물',
            content='# 제목\n\n내용',
            author_id=user.id,
            category_id=category.id
        )
        post.save()

        assert post.id is not None
        assert post.published == False
        assert post.view_count == 0

        # 발행
        post.publish()
        assert post.published == True
        assert post.published_at is not None
```

**실행**:
```bash
pytest tests/test_models.py -v
```

---

## 다음 단계

Phase 2 완료 후:
1. **Git 커밋**
2. **Phase 3로 이동**: [Phase 3: Flask API 구조](./phase-03.md)

---

**완료 기준**:
- 모든 테이블 생성 확인
- 모델 간 관계 정상 작동
- 시드 데이터 생성 성공
- 테스트 통과
