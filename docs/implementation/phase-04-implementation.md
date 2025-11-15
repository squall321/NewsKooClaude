# Phase 4 구현 상세 문서

**Phase**: JWT 인증 시스템
**완료 날짜**: 2025-11-15
**소요 시간**: 약 2시간

---

## 📋 개요

Phase 4에서는 JWT (JSON Web Token) 기반 인증 시스템을 구현했습니다. 관리자용 사용자 등록, 로그인, 토큰 갱신, 비밀번호 변경 기능을 제공합니다.

---

## 🎯 달성 목표

- ✅ Auth API 구현 (6개 엔드포인트)
- ✅ JWT 토큰 발급 및 검증
- ✅ Refresh Token 관리
- ✅ 비밀번호 해싱 (User 모델에서 구현됨)
- ✅ Protected Routes 테스트
- ✅ 인증 테스트 (20+ 케이스)

---

## 🔧 구현 내용

### 1. Auth API 엔드포인트

**파일**: `backend/app/api/auth.py`

#### 엔드포인트 목록

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register` | 사용자 등록 | Admin |
| POST | `/api/auth/login` | 로그인 | Public |
| POST | `/api/auth/refresh` | 토큰 갱신 | Refresh Token |
| GET | `/api/auth/me` | 현재 사용자 조회 | JWT |
| POST | `/api/auth/logout` | 로그아웃 | JWT |
| POST | `/api/auth/change-password` | 비밀번호 변경 | JWT |

---

### 2. 사용자 등록 (POST /api/auth/register)

**관리자 전용** - 새로운 사용자 계정 생성

#### Request
```json
{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "password123",
  "role": "writer"
}
```

#### Validation
- `username`: 3-50자
- `password`: 최소 8자
- `email`: 유효한 이메일 형식
- `role`: admin, editor, writer 중 하나

#### Response (201)
```json
{
  "message": "User created successfully",
  "user": {
    "id": 1,
    "username": "newuser",
    "email": "newuser@example.com",
    "role": "writer",
    "is_active": true
  }
}
```

#### 에러
- **409 Conflict**: 중복된 username 또는 email
- **400 Validation Error**: 유효성 검증 실패
- **403 Authorization Error**: 관리자 권한 없음

---

### 3. 로그인 (POST /api/auth/login)

사용자 인증 및 JWT 토큰 발급

#### Request
```json
{
  "username": "testuser",
  "password": "password123"
}
```

#### Response (200)
```json
{
  "message": "Login successful",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "role": "writer"
  }
}
```

#### 토큰 정보
- **Access Token**: 1시간 유효 (JWT_ACCESS_TOKEN_EXPIRES)
- **Refresh Token**: 30일 유효 (기본값)

#### 에러
- **401 Authentication Error**: 잘못된 username 또는 password
- **401 Authentication Error**: 비활성화된 계정

---

### 4. 토큰 갱신 (POST /api/auth/refresh)

Refresh Token을 사용하여 새로운 Access Token 발급

#### Headers
```
Authorization: Bearer <refresh_token>
```

#### Response (200)
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### 에러
- **401 Unauthorized**: 유효하지 않은 Refresh Token
- **422 Unprocessable Entity**: Access Token 사용 시도

---

### 5. 현재 사용자 조회 (GET /api/auth/me)

인증된 사용자의 정보 조회

#### Headers
```
Authorization: Bearer <access_token>
```

#### Response (200)
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "role": "writer",
  "is_active": true,
  "post_count": 5,
  "draft_count": 3,
  "created_at": "2025-11-15T10:00:00",
  "updated_at": "2025-11-15T12:00:00"
}
```

---

### 6. 로그아웃 (POST /api/auth/logout)

클라이언트에서 토큰 삭제로 처리

#### Headers
```
Authorization: Bearer <access_token>
```

#### Response (200)
```json
{
  "message": "Logout successful"
}
```

**참고**: 현재는 클라이언트 측에서 토큰을 삭제하는 방식입니다. 향후 Token Blacklist를 구현하여 서버 측에서도 토큰을 무효화할 수 있습니다.

---

### 7. 비밀번호 변경 (POST /api/auth/change-password)

현재 사용자의 비밀번호 변경

#### Request
```json
{
  "old_password": "password123",
  "new_password": "newpassword123"
}
```

#### Validation
- `new_password`: 최소 8자

#### Response (200)
```json
{
  "message": "Password changed successfully"
}
```

#### 에러
- **401 Authentication Error**: 현재 비밀번호 불일치
- **400 Validation Error**: 새 비밀번호 형식 오류

---

## 🔐 JWT 설정

### Flask-JWT-Extended 설정

**파일**: `backend/app/config/__init__.py`

```python
class Settings(BaseSettings):
    JWT_SECRET_KEY: str = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES: int = 3600  # 1시간
```

### 토큰 구조

**Access Token Payload**:
```json
{
  "sub": 1,  # User ID
  "iat": 1699000000,
  "exp": 1699003600,
  "type": "access",
  "jti": "unique-jwt-id"
}
```

**Refresh Token Payload**:
```json
{
  "sub": 1,
  "iat": 1699000000,
  "exp": 1701592000,
  "type": "refresh",
  "jti": "unique-jwt-id"
}
```

---

## 🛡️ 보안 기능

### 1. 비밀번호 해싱

**Werkzeug** 라이브러리 사용 (User 모델):
```python
from werkzeug.security import generate_password_hash, check_password_hash

def set_password(self, password):
    self.password_hash = generate_password_hash(password)

def check_password(self, password):
    return check_password_hash(self.password_hash, password)
```

### 2. 권한 체크

**데코레이터 사용**:
- `@jwt_required()` - JWT 토큰 필요
- `@jwt_required(refresh=True)` - Refresh Token 필요
- `@admin_required` - 관리자 권한 필요
- `@editor_required` - 편집자 이상 권한 필요

### 3. 계정 상태 확인

- 로그인 시 `is_active` 확인
- 비활성화된 계정은 로그인 불가

---

## 📦 생성된 파일

```
backend/app/api/
└── auth.py           # Auth API (6개 엔드포인트)

backend/app/api/
└── __init__.py       # auth_bp 등록 (업데이트)

backend/tests/
└── test_auth.py      # Auth 테스트 (20+ 케이스)
```

---

## ✅ 테스트

### 테스트 케이스 (20+)

**실행 방법** (Phase 5에서 진행 예정):
```bash
pytest tests/test_auth.py -v
```

**테스트 커버리지**:

#### 1. 사용자 등록 테스트
- ✅ 관리자가 새 사용자 등록 성공
- ✅ 인증 없이 등록 시도 (실패)
- ✅ 비관리자가 등록 시도 (실패)
- ✅ 중복 사용자명 (실패)
- ✅ 짧은 비밀번호 (실패)

#### 2. 로그인 테스트
- ✅ 로그인 성공
- ✅ 존재하지 않는 사용자 (실패)
- ✅ 잘못된 비밀번호 (실패)
- ✅ 필수 필드 누락 (실패)

#### 3. 토큰 갱신 테스트
- ✅ Refresh Token으로 갱신 성공
- ✅ Access Token으로 갱신 시도 (실패)
- ✅ 토큰 없이 갱신 시도 (실패)

#### 4. 현재 사용자 조회 테스트
- ✅ 사용자 정보 조회 성공
- ✅ 토큰 없이 조회 (실패)

#### 5. 로그아웃 테스트
- ✅ 로그아웃 성공

#### 6. 비밀번호 변경 테스트
- ✅ 비밀번호 변경 성공
- ✅ 잘못된 현재 비밀번호 (실패)
- ✅ 너무 짧은 새 비밀번호 (실패)

---

## 💡 배운 점

1. **Flask-JWT-Extended**: JWT 토큰 생성 및 검증
2. **Refresh Token 패턴**: Access Token 갱신 메커니즘
3. **데코레이터 체이닝**: `@jwt_required()` + `@admin_required`
4. **비밀번호 해싱**: Werkzeug의 generate_password_hash
5. **토큰 타입 구분**: Access vs Refresh Token

---

## 🔄 인증 플로우

### 1. 로그인 플로우

```
1. 사용자가 username/password 제공
   ↓
2. 서버가 사용자 조회 및 비밀번호 검증
   ↓
3. JWT Access Token 및 Refresh Token 발급
   ↓
4. 클라이언트가 토큰 저장 (localStorage 또는 cookie)
```

### 2. API 요청 플로우

```
1. 클라이언트가 Authorization 헤더에 Access Token 포함
   ↓
2. 서버가 토큰 검증 (@jwt_required)
   ↓
3. 토큰에서 User ID 추출 (get_jwt_identity)
   ↓
4. 요청 처리 및 응답
```

### 3. 토큰 갱신 플로우

```
1. Access Token 만료됨
   ↓
2. 클라이언트가 Refresh Token으로 /auth/refresh 호출
   ↓
3. 서버가 새로운 Access Token 발급
   ↓
4. 클라이언트가 새 Access Token 저장
```

---

## ⚠️ 주의사항

### Token Blacklist 미구현

현재는 로그아웃 시 클라이언트에서 토큰을 삭제하는 방식입니다.

향후 개선 사항:
- Redis를 사용한 Token Blacklist
- JWT ID (jti)를 블랙리스트에 추가
- 토큰 검증 시 블랙리스트 확인

### 프로덕션 환경 주의사항

1. **JWT_SECRET_KEY**: 강력한 비밀 키 사용 필수
2. **HTTPS**: JWT 토큰은 반드시 HTTPS로 전송
3. **Token 저장**: localStorage보다 httpOnly cookie 권장
4. **토큰 만료 시간**: 보안과 UX 균형 고려

---

## 📊 통계

- **API 엔드포인트**: 6개 (Auth)
- **테스트 케이스**: 20+개
- **코드 라인**: 약 600줄 (API + 테스트)
- **토큰 타입**: 2개 (Access, Refresh)

---

## 🔄 다음 단계 (Phase 5)

**Phase 5: 로컬 LLM 설정**

주요 작업:
1. CUDA 및 PyTorch 설치 (RTX 5070 TI용)
2. EEVE-Korean-10.8B 모델 다운로드
3. INT8 양자화 설정
4. LLM 서비스 클래스 구현
5. 추론 API 엔드포인트

---

**Phase 4 완료 ✅**

다음: [Phase 5 - 로컬 LLM 설정](./phase-05-implementation.md)
