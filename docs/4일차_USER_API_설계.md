# User API 설계 명세서

> 흉부 X-Ray AI 진단 서비스 - 사용자 관련 API 명세서  
> 기준 요구사항: REQ-USER-001 ~ REQ-USER-009, NFR-USER-001 ~ NFR-USER-003

---

## API 목록

| No | 요구사항 ID | API 명 | Method | Endpoint |
| --- | --- | --- | --- | --- |
| 1 | REQ-USER-001 | 회원가입 | POST | `/api/v1/users/register/` |
| 2 | REQ-USER-002, NFR-USER-001 | 로그인 | POST | `/api/v1/auth/login/` |
| 3 | NFR-USER-001 | 토큰 재발급 | POST | `/api/v1/auth/token/refresh/` |
| 4 | REQ-USER-003 | 로그아웃 | POST | `/api/v1/auth/logout/` |
| 5 | REQ-USER-004 | 회원 목록 조회 | GET | `/api/v1/users/` |
| 6 | REQ-USER-005 | 회원 권한 변경 | PATCH | `/api/v1/users/{user_id}/role/` |
| 7 | REQ-USER-006 | 마이페이지 조회 | GET | `/api/v1/users/me/` |
| 8 | REQ-USER-007 | 회원 정보 수정 | PATCH | `/api/v1/users/me/` |
| 9 | REQ-USER-008 | 비밀번호 변경 | PUT | `/api/v1/users/me/password/` |
| 10 | REQ-USER-009 | 회원 탈퇴 | DELETE | `/api/v1/users/me/` |

---

## 공통 사항

### 인증 방식
- 인증이 필요한 API는 요청 헤더에 JWT 액세스 토큰을 포함해야 합니다.
- `Authorization: Bearer <access_token>`
- 액세스 토큰 만료 주기: **30분**
- 리프레시 토큰 만료 주기: **7일** (http_only 쿠키로 전달)
- JWT 페이로드에는 `user_id`만 저장합니다.

### 권한(Role) 정의
| 권한 | 설명 |
| --- | --- |
| `pending` | 대기자 (신규 가입 기본값) |
| `staff` | 스태프 |
| `admin` | 어드민 (관리자) |

### 부서(Department) 정의
| 값 | 설명 |
| --- | --- |
| `research` | 연구 |
| `medical` | 의료 |
| `development` | 개발 |

### 성능 기준 (NFR-USER-003)
- 모든 유저 API는 최대 **3초 이내** 응답을 보장해야 합니다.

### 공통 에러 응답
| HTTP 상태코드 | 설명 |
| --- | --- |
| 400 Bad Request | 요청 데이터 유효성 오류 |
| 401 Unauthorized | 인증 토큰 없음 또는 만료 |
| 403 Forbidden | 권한 없음 |
| 404 Not Found | 리소스 없음 |
| 500 Internal Server Error | 서버 내부 오류 |

---

## 1. 회원가입 API

| 항목 | 내용 |
| --- | --- |
| API 이름 | 회원가입 API |
| 설명 | 이메일, 비밀번호 등 사용자 정보를 입력하여 회원가입을 진행하는 API |
| 엔드포인트(Endpoint) | `/api/v1/users/register/` |
| 메서드(Method) | `POST` |
| 인증 필요 여부 | N |

### 요청(Request)

#### Headers
| Key | Value | 설명 |
| --- | --- | --- |
| Content-Type | application/json | 요청 타입 |

#### 본문 예시
```json
{
  "email": "example@company.com",
  "password": "securepassword123!",
  "name": "홍길동",
  "department": "medical",
  "gender": "M",
  "phone_number": "010-1234-5678"
}
```

#### 본문 필드
| 파라미터명 | 타입 | 필수 (Y/N) | 설명 |
| --- | --- | --- | --- |
| email | string | Y | 사용자 이메일 (고유값) |
| password | string | Y | 사용자 비밀번호 |
| name | string | Y | 사용자 이름 |
| department | string | Y | 부서 (`research` / `medical` / `development`) |
| gender | string | Y | 성별 (`M` / `F`) |
| phone_number | string | Y | 휴대폰 번호 |

### 응답(Response)

#### 성공
- **201 Created**
```json
{
  "id": 1,
  "email": "example@company.com",
  "name": "홍길동",
  "department": "medical",
  "gender": "M",
  "phone_number": "010-1234-5678",
  "role": "pending"
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| id | integer | 사용자 고유 ID |
| email | string | 사용자 이메일 |
| name | string | 사용자 이름 |
| department | string | 부서 |
| gender | string | 성별 |
| phone_number | string | 휴대폰 번호 |
| role | string | 권한 (가입 시 `pending` 기본값) |

#### 실패
- **400 Bad Request**
```json
{
  "detail": "이미 사용 중인 이메일입니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | `duplicate_email` : 이메일 중복 / `empty_fields` : 필수 필드 누락 / `invalid_field_value` : 필드 값 형식 오류 |

### 비고
- 비밀번호는 암호화(해시)하여 DB에 저장합니다.
- 회원가입 직후 권한은 `pending(대기자)`으로 설정됩니다.

---

## 2. 로그인 API

| 항목 | 내용 |
| --- | --- |
| API 이름 | 로그인 API |
| 설명 | 이메일, 비밀번호를 통해 로그인하고 JWT 토큰을 발급하는 API |
| 엔드포인트(Endpoint) | `/api/v1/auth/login/` |
| 메서드(Method) | `POST` |
| 인증 필요 여부 | N |

### 요청(Request)

#### Headers
| Key | Value | 설명 |
| --- | --- | --- |
| Content-Type | application/json | 요청 타입 |

#### 본문 예시
```json
{
  "email": "example@company.com",
  "password": "securepassword123!"
}
```

#### 본문 필드
| 파라미터명 | 타입 | 필수 (Y/N) | 설명 |
| --- | --- | --- | --- |
| email | string | Y | 사용자 이메일 |
| password | string | Y | 사용자 비밀번호 |

### 응답(Response)

#### 성공
- **200 OK**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "email": "example@company.com",
    "name": "홍길동",
    "role": "staff"
  }
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| access_token | string | JWT 액세스 토큰 (만료: 30분) |
| user | object | 사용자 기본 정보 |
| user.id | integer | 사용자 고유 ID |
| user.email | string | 사용자 이메일 |
| user.name | string | 사용자 이름 |
| user.role | string | 사용자 권한 |

#### 실패
- **400 Bad Request**
```json
{
  "detail": "이메일 또는 비밀번호가 일치하지 않습니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | `invalid_email_or_password` : 이메일 혹은 비밀번호 불일치 / `empty_fields` : 필수 필드 누락 |

### 비고
- 리프레시 토큰은 `http_only` 쿠키로 전달되어 클라이언트 스크립트에서 접근할 수 없습니다.
- JWT 페이로드에는 `user_id`만 포함됩니다.

---

## 3. 토큰 재발급 API

| 항목 | 내용 |
| --- | --- |
| API 이름 | 액세스 토큰 재발급 API |
| 설명 | 리프레시 토큰을 통해 만료된 액세스 토큰을 재발급하는 API |
| 엔드포인트(Endpoint) | `/api/v1/auth/token/refresh/` |
| 메서드(Method) | `POST` |
| 인증 필요 여부 | N (리프레시 토큰 쿠키 필요) |

### 요청(Request)

#### Headers
| Key | Value | 설명 |
| --- | --- | --- |
| Content-Type | application/json | 요청 타입 |
| Cookie | refresh_token=`<refresh_token>` | http_only 쿠키로 자동 전달 |

#### 본문 예시
```json
{}
```
> 리프레시 토큰은 http_only 쿠키로 자동 전달되므로 본문 없이 요청합니다.

### 응답(Response)

#### 성공
- **200 OK**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| access_token | string | 새로 발급된 JWT 액세스 토큰 (만료: 30분) |

#### 실패
- **401 Unauthorized**
```json
{
  "detail": "리프레시 토큰이 만료되었습니다. 다시 로그인해 주세요."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | `refresh_token_expired` : 리프레시 토큰 만료 / `invalid_refresh_token` : 유효하지 않은 리프레시 토큰 |

### 비고
- 리프레시 토큰이 만료된 경우 재로그인이 필요합니다.

---

## 4. 로그아웃 API

| 항목 | 내용 |
| --- | --- |
| API 이름 | 로그아웃 API |
| 설명 | 로그인된 사용자의 세션을 종료하고 리프레시 토큰을 무효화하는 API |
| 엔드포인트(Endpoint) | `/api/v1/auth/logout/` |
| 메서드(Method) | `POST` |
| 인증 필요 여부 | Y |

### 요청(Request)

#### Headers
| Key | Value | 설명 |
| --- | --- | --- |
| Content-Type | application/json | 요청 타입 |
| Authorization | Bearer `<access_token>` | JWT 액세스 토큰 |

#### 본문 예시
```json
{}
```

### 응답(Response)

#### 성공
- **200 OK**
```json
{
  "detail": "정상적으로 로그아웃 되었습니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | 로그아웃 성공 메시지 |

#### 실패
- **401 Unauthorized**
```json
{
  "detail": "인증 토큰이 유효하지 않습니다."
}
```

### 비고
- 로그아웃 시 서버에서 리프레시 토큰을 무효화하고 http_only 쿠키를 삭제합니다.
- 클라이언트는 로그아웃 후 로그인 페이지로 리다이렉트합니다.

---

## 5. 회원 목록 조회 API

| 항목 | 내용 |
| --- | --- |
| API 이름 | 회원 목록 조회 API |
| 설명 | 관리자(Admin)가 전체 회원 목록을 조회하는 API. 이메일/이름 검색 및 부서 필터 지원 |
| 엔드포인트(Endpoint) | `/api/v1/users/` |
| 메서드(Method) | `GET` |
| 인증 필요 여부 | Y (Admin 권한 필요) |

### 요청(Request)

#### Headers
| Key | Value | 설명 |
| --- | --- | --- |
| Authorization | Bearer `<access_token>` | JWT 액세스 토큰 (Admin 권한) |

#### 쿼리 파라미터
| 쿼리 파라미터명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| search | string | N | 이메일 또는 이름으로 검색 |
| department | string | N | 부서 필터 (`research` / `medical` / `development`) |

#### 요청 예시
```
GET /api/v1/users/?search=홍길동&department=medical
```

### 응답(Response)

#### 성공
- **200 OK**
```json
{
  "count": 2,
  "results": [
    {
      "id": 1,
      "email": "hong@company.com",
      "name": "홍길동",
      "department": "medical",
      "gender": "M",
      "phone_number": "010-1234-5678",
      "is_active": true,
      "role": "staff"
    },
    {
      "id": 2,
      "email": "kim@company.com",
      "name": "김철수",
      "department": "medical",
      "gender": "M",
      "phone_number": "010-9876-5432",
      "is_active": true,
      "role": "pending"
    }
  ]
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| count | integer | 전체 결과 수 |
| results | array | 회원 목록 |
| results[].id | integer | 사용자 고유 ID |
| results[].email | string | 이메일 |
| results[].name | string | 이름 |
| results[].department | string | 부서 |
| results[].gender | string | 성별 |
| results[].phone_number | string | 휴대폰 번호 |
| results[].is_active | boolean | 계정 활성화 여부 |
| results[].role | string | 권한 |

#### 실패
- **401 Unauthorized**
```json
{
  "detail": "인증 토큰이 유효하지 않습니다."
}
```
- **403 Forbidden**
```json
{
  "detail": "관리자 권한이 필요합니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | `unauthorized` : 인증 실패 / `forbidden` : 권한 없음 |

### 비고
- 관리자(`admin`) 권한을 가진 사용자만 접근 가능합니다.

---

## 6. 회원 권한 변경 API

| 항목 | 내용 |
| --- | --- |
| API 이름 | 회원 권한 변경 API |
| 설명 | 관리자(Admin)가 특정 회원의 권한을 변경하는 API |
| 엔드포인트(Endpoint) | `/api/v1/users/{user_id}/role/` |
| 메서드(Method) | `PATCH` |
| 인증 필요 여부 | Y (Admin 권한 필요) |

### 요청(Request)

#### Headers
| Key | Value | 설명 |
| --- | --- | --- |
| Content-Type | application/json | 요청 타입 |
| Authorization | Bearer `<access_token>` | JWT 액세스 토큰 (Admin 권한) |

#### 경로 파라미터
| 파라미터명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| user_id | integer | Y | 권한을 변경할 대상 사용자의 고유 ID |

#### 본문 예시
```json
{
  "role": "staff"
}
```

#### 본문 필드
| 파라미터명 | 타입 | 필수 (Y/N) | 설명 |
| --- | --- | --- | --- |
| role | string | Y | 변경할 권한 (`pending` / `staff` / `admin`) |

### 응답(Response)

#### 성공
- **200 OK**
```json
{
  "id": 2,
  "email": "kim@company.com",
  "name": "김철수",
  "role": "staff"
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| id | integer | 사용자 고유 ID |
| email | string | 이메일 |
| name | string | 이름 |
| role | string | 변경된 권한 |

#### 실패
- **400 Bad Request**
```json
{
  "detail": "유효하지 않은 권한 값입니다."
}
```
- **403 Forbidden**
```json
{
  "detail": "관리자 권한이 필요합니다."
}
```
- **404 Not Found**
```json
{
  "detail": "해당 사용자를 찾을 수 없습니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | `invalid_role` : 유효하지 않은 권한 값 / `forbidden` : 권한 없음 / `user_not_found` : 사용자 없음 |

### 비고
- 관리자(`admin`) 권한을 가진 사용자만 접근 가능합니다.

---

## 7. 마이페이지 조회 API

| 항목 | 내용 |
| --- | --- |
| API 이름 | 마이페이지 조회 API |
| 설명 | 로그인한 사용자 본인의 정보를 조회하는 API |
| 엔드포인트(Endpoint) | `/api/v1/users/me/` |
| 메서드(Method) | `GET` |
| 인증 필요 여부 | Y |

### 요청(Request)

#### Headers
| Key | Value | 설명 |
| --- | --- | --- |
| Authorization | Bearer `<access_token>` | JWT 액세스 토큰 |

### 응답(Response)

#### 성공
- **200 OK**
```json
{
  "id": 1,
  "email": "hong@company.com",
  "name": "홍길동",
  "department": "medical",
  "gender": "M",
  "phone_number": "010-1234-5678",
  "role": "staff"
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| id | integer | 사용자 고유 ID |
| email | string | 이메일 |
| name | string | 이름 |
| department | string | 부서 |
| gender | string | 성별 |
| phone_number | string | 휴대폰 번호 |
| role | string | 권한 |

#### 실패
- **401 Unauthorized**
```json
{
  "detail": "인증 토큰이 유효하지 않습니다."
}
```

---

## 8. 회원 정보 수정 API

| 항목 | 내용 |
| --- | --- |
| API 이름 | 회원 정보 수정 API |
| 설명 | 로그인한 사용자가 본인의 부서 및 휴대폰 번호를 수정하는 API (Partial Update) |
| 엔드포인트(Endpoint) | `/api/v1/users/me/` |
| 메서드(Method) | `PATCH` |
| 인증 필요 여부 | Y |

### 요청(Request)

#### Headers
| Key | Value | 설명 |
| --- | --- | --- |
| Content-Type | application/json | 요청 타입 |
| Authorization | Bearer `<access_token>` | JWT 액세스 토큰 |

#### 본문 예시
```json
{
  "department": "development",
  "phone_number": "010-0000-1111"
}
```

#### 본문 필드
| 파라미터명 | 타입 | 필수 (Y/N) | 설명 |
| --- | --- | --- | --- |
| department | string | N | 부서 (`research` / `medical` / `development`) |
| phone_number | string | N | 휴대폰 번호 |

> 두 필드 중 하나 이상 포함해야 합니다.

### 응답(Response)

#### 성공
- **200 OK**
```json
{
  "id": 1,
  "email": "hong@company.com",
  "name": "홍길동",
  "department": "development",
  "gender": "M",
  "phone_number": "010-0000-1111",
  "role": "staff"
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| id | integer | 사용자 고유 ID |
| email | string | 이메일 |
| name | string | 이름 |
| department | string | 수정된 부서 |
| gender | string | 성별 |
| phone_number | string | 수정된 휴대폰 번호 |
| role | string | 권한 |

#### 실패
- **400 Bad Request**
```json
{
  "detail": "수정 가능한 필드가 포함되어 있지 않습니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | `no_updatable_fields` : 수정 가능한 필드 없음 / `invalid_field_value` : 필드 값 형식 오류 |

### 비고
- PATCH 방식으로 동작하므로 수정할 필드만 포함하여 요청합니다.
- 수정 가능한 항목은 `department`, `phone_number`로 제한됩니다.

---

## 9. 비밀번호 변경 API

| 항목 | 내용 |
| --- | --- |
| API 이름 | 비밀번호 변경 API |
| 설명 | 로그인한 사용자가 기존 비밀번호를 검증 후 새 비밀번호로 변경하는 API |
| 엔드포인트(Endpoint) | `/api/v1/users/me/password/` |
| 메서드(Method) | `PUT` |
| 인증 필요 여부 | Y |

### 요청(Request)

#### Headers
| Key | Value | 설명 |
| --- | --- | --- |
| Content-Type | application/json | 요청 타입 |
| Authorization | Bearer `<access_token>` | JWT 액세스 토큰 |

#### 본문 예시
```json
{
  "current_password": "oldpassword123!",
  "new_password": "newpassword456!"
}
```

#### 본문 필드
| 파라미터명 | 타입 | 필수 (Y/N) | 설명 |
| --- | --- | --- | --- |
| current_password | string | Y | 기존 비밀번호 |
| new_password | string | Y | 변경할 새 비밀번호 |

### 응답(Response)

#### 성공
- **200 OK**
```json
{
  "detail": "비밀번호가 성공적으로 변경되었습니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | 변경 성공 메시지 |

#### 실패
- **400 Bad Request**
```json
{
  "detail": "기존 비밀번호가 일치하지 않습니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | `wrong_current_password` : 기존 비밀번호 불일치 / `empty_fields` : 필수 필드 누락 / `same_as_current` : 새 비밀번호가 기존 비밀번호와 동일한 경우 |

### 비고
- 새 비밀번호는 암호화(해시)하여 DB에 저장합니다.
- 비밀번호 입력 필드는 클라이언트에서 마스킹 처리합니다. (NFR-USER-002)

---

## 10. 회원 탈퇴 API

| 항목 | 내용 |
| --- | --- |
| API 이름 | 회원 탈퇴 API |
| 설명 | 로그인한 사용자가 본인 계정을 탈퇴하는 API. 탈퇴 즉시 DB에서 모든 관련 데이터 삭제 |
| 엔드포인트(Endpoint) | `/api/v1/users/me/` |
| 메서드(Method) | `DELETE` |
| 인증 필요 여부 | Y |

### 요청(Request)

#### Headers
| Key | Value | 설명 |
| --- | --- | --- |
| Content-Type | application/json | 요청 타입 |
| Authorization | Bearer `<access_token>` | JWT 액세스 토큰 |

#### 본문 예시
```json
{
  "password": "securepassword123!"
}
```

#### 본문 필드
| 파라미터명 | 타입 | 필수 (Y/N) | 설명 |
| --- | --- | --- | --- |
| password | string | Y | 본인 확인을 위한 비밀번호 |

### 응답(Response)

#### 성공
- **204 No Content**

#### 실패
- **400 Bad Request**
```json
{
  "detail": "비밀번호가 일치하지 않습니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | `wrong_password` : 비밀번호 불일치 / `empty_fields` : 필수 필드 누락 |

### 비고
- 탈퇴 시 해당 사용자와 관련된 **모든 데이터를 즉시 DB에서 삭제(Hard Delete)** 합니다.
- 탈퇴 처리 후 서버에서 리프레시 토큰을 무효화하고 http_only 쿠키를 삭제합니다.
