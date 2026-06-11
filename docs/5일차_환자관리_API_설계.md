# 환자 관리 및 진료기록 API 설계 명세서

> 흉부 X-Ray AI 진단 서비스 - 환자 관리 및 진료기록 관련 API 명세서
> 기준 요구사항: REQ-PTNT-001 ~ REQ-PTNT-005, REQ-MDR-001 ~ REQ-MDR-003, NFR-PTNT-001, NFR-MDR-001

---

## API 목록

| No | 요구사항 ID      | API 명          | Method | Endpoint                                                     |
| -- | ------------ | -------------- | ------ | ------------------------------------------------------------ |
| 1  | REQ-PTNT-001 | 환자 정보 등록       | POST   | `/api/v1/patients/`                                          |
| 2  | REQ-PTNT-002 | 환자 목록 조회       | GET    | `/api/v1/patients/`                                          |
| 3  | REQ-PTNT-003 | 환자 상세 조회       | GET    | `/api/v1/patients/{patient_id}/`                             |
| 4  | REQ-PTNT-004 | 환자 정보 수정       | PATCH  | `/api/v1/patients/{patient_id}/`                             |
| 5  | REQ-PTNT-005 | 환자 정보 삭제       | DELETE | `/api/v1/patients/{patient_id}/`                             |
| 6  | REQ-MDR-001  | 진료기록 등록        | POST   | `/api/v1/patients/{patient_id}/medical-records/`             |
| 7  | REQ-MDR-002  | 환자별 진료기록 목록 조회 | GET    | `/api/v1/patients/{patient_id}/medical-records/`             |
| 8  | REQ-MDR-003  | 진료기록 상세 조회     | GET    | `/api/v1/patients/{patient_id}/medical-records/{record_id}/` |

---

## 설계 범위

본 문서는 요구사항 정의서에 명시된 환자 정보 등록, 목록 조회, 상세 조회, 수정, 삭제 API와 진료기록 등록, 목록 조회, 상세 조회 API를 정의한다.

제공된 요구사항 정의서에는 진료기록 수정 및 삭제 요구사항이 별도로 명시되어 있지 않으므로, 본 명세에서는 임의로 진료기록 수정 및 삭제 API를 추가하지 않는다.

모든 환자 및 진료기록 API는 인증된 사내 사용자를 대상으로 하며, 각 기능의 권한 조건은 요구사항에 따라 구분한다.

---

## 공통 사항

### 인증 방식

* 모든 환자 및 진료기록 API는 로그인이 필요합니다.
* 요청 헤더에 JWT 액세스 토큰을 포함해야 합니다.
* `Authorization: Bearer <access_token>`
* 인증 토큰이 없거나 유효하지 않으면 `401 Unauthorized`를 반환합니다.

### 권한 기준

| 구분       | 허용 대상                                                    | 적용 API               |
| -------- | -------------------------------------------------------- | -------------------- |
| 환자 정보 등록 | `department=medical`이며 `role=staff` 또는 `role=admin`인 사용자 | 환자 정보 등록             |
| 진료기록 등록  | `department=medical`이며 `role=staff` 또는 `role=admin`인 사용자 | 진료기록 등록              |
| 조회·수정·삭제 | 개발·의료·연구 부서의 `role=staff` 또는 `role=admin` 사용자            | 환자 조회·수정·삭제, 진료기록 조회 |

본 명세에서 요구사항의 “사내 의료인 역할”은 `department=medical`이면서 `role=staff` 또는 `role=admin`인 사용자로 해석합니다.

요구사항의 “로그인된 사내 개발진, 의료 실무진, 연구진”은 각 부서에 소속되어 있고 `role=staff` 또는 `role=admin` 권한을 부여받은 사용자로 해석합니다.

`role=pending` 사용자는 권한 부여 대기 상태이므로 환자 및 진료기록 API에 접근할 수 없습니다.


### 성별 값

| 값   | 설명 |
| --- | -- |
| `M` | 남성 |
| `F` | 여성 |

### 데이터 형식

* 일반적인 요청과 응답은 `application/json` 형식을 사용합니다.
* X-ray 이미지가 포함된 진료기록 등록 요청은 `multipart/form-data` 형식을 사용합니다.
* 날짜와 시간은 ISO 8601 형식으로 반환합니다.
* 예시: `2026-06-11T15:30:00`

### 성능 기준

* `NFR-PTNT-001`에 따라 모든 환자 API는 최대 3초 이내에 처리하고 응답해야 합니다.
* `NFR-MDR-001`에 따라 모든 진료기록 API는 최대 3초 이내에 처리하고 응답해야 합니다.

### 공통 에러 응답

| HTTP 상태코드                 | 설명                       |
| ------------------------- | ------------------------ |
| 400 Bad Request           | 요청값 또는 요청 처리 조건이 올바르지 않음 |
| 401 Unauthorized          | 인증 토큰이 없거나 만료됨           |
| 403 Forbidden             | 해당 기능을 수행할 권한이 없음        |
| 404 Not Found             | 환자 또는 진료기록을 찾을 수 없음      |
| 409 Conflict              | 차트 번호 등 고유값이 이미 존재함      |
| 422 Unprocessable Entity  | 요청 필드의 형식 또는 유효성 검증 실패   |
| 500 Internal Server Error | 서버 내부 오류                 |

공통 에러 응답 형식은 다음과 같습니다.

```json
{
  "detail": "오류 메시지"
}
```

---

## 1. 환자 정보 등록 API

| 항목              | 내용                                                    |
| --------------- | ----------------------------------------------------- |
| 요구사항 ID         | `REQ-PTNT-001`                                        |
| API 이름          | 환자 정보 등록 API                                          |
| 설명              | 의료인 권한을 가진 사용자가 이름, 나이, 성별, 연락처를 입력하여 환자 정보를 등록하는 API |
| 엔드포인트(Endpoint) | `/api/v1/patients/`                                   |
| 메서드(Method)     | `POST`                                                |
| 인증 필요 여부        | Y                                                     |
| 허용 권한           | 의료 부서 소속의 `staff`, `admin`                            |

### 요청(Request)

#### Headers

| Key           | Value                   | 설명         |
| ------------- | ----------------------- | ---------- |
| Authorization | `Bearer <access_token>` | JWT 액세스 토큰 |
| Content-Type  | `application/json`      | 요청 데이터 형식  |

#### 본문 예시

```json
{
  "name": "김환자",
  "age": 65,
  "gender": "M",
  "phone": "01012345678"
}
```

#### 본문 필드

| 파라미터명  | 타입      | 필수 (Y/N) | 설명                       |
| ------ | ------- | -------- | ------------------------ |
| name   | string  | Y        | 환자 이름, 최대 30자            |
| age    | integer | Y        | 환자 나이, 0 이상의 정수          |
| gender | string  | Y        | 환자 성별, `M` 또는 `F`        |
| phone  | string  | Y        | 국내 휴대폰 번호, 하이픈을 제외한 11자리 |

### 응답(Response)

#### 성공

* `201 Created`

```json
{
  "id": 1,
  "name": "김환자",
  "age": 65,
  "gender": "M",
  "phone": "01012345678",
  "created_at": "2026-06-11T15:30:00",
  "updated_at": null
}
```

#### 응답 필드

| 필드명        | 타입               | 설명          |
| ---------- | ---------------- | ----------- |
| id         | integer          | 환자 고유 ID    |
| name       | string           | 환자 이름       |
| age        | integer          | 환자 나이       |
| gender     | string           | 환자 성별       |
| phone      | string           | 환자 연락처      |
| created_at | datetime         | 환자 정보 등록 일시 |
| updated_at | datetime 또는 null | 환자 정보 수정 일시 |

#### 실패

* `401 Unauthorized`: 인증 토큰이 없거나 유효하지 않은 경우
* `403 Forbidden`: 환자 등록 권한이 없는 경우
* `422 Unprocessable Entity`: 필수값이 누락되었거나 입력값 형식이 올바르지 않은 경우

```json
{
  "detail": "환자 정보를 등록할 권한이 없습니다."
}
```

---

## 2. 환자 목록 조회 API

| 항목              | 내용                                                        |
| --------------- | --------------------------------------------------------- |
| 요구사항 ID         | `REQ-PTNT-002`                                            |
| API 이름          | 환자 목록 조회 API                                              |
| 설명              | 로그인한 사내 사용자가 등록된 환자 목록을 조회하고, 이름·성별·나이 범위로 검색 및 필터링하는 API |
| 엔드포인트(Endpoint) | `/api/v1/patients/`                                       |
| 메서드(Method)     | `GET`                                                     |
| 인증 필요 여부        | Y                                                         |
| 허용 권한           | `staff`, `admin`                                          |

### 요청(Request)

#### Headers

| Key           | Value                   | 설명         |
| ------------- | ----------------------- | ---------- |
| Authorization | `Bearer <access_token>` | JWT 액세스 토큰 |

#### Query Parameters

| 파라미터명   | 타입      | 필수 (Y/N) | 기본값 | 설명                |
| ------- | ------- | -------- | --- | ----------------- |
| name    | string  | N        | 없음  | 환자 이름 검색어         |
| gender  | string  | N        | 없음  | 성별 필터, `M` 또는 `F` |
| min_age | integer | N        | 없음  | 조회할 최소 나이         |
| max_age | integer | N        | 없음  | 조회할 최대 나이         |
| page    | integer | N        | 1   | 조회할 페이지 번호        |
| size    | integer | N        | 20  | 한 페이지에 조회할 환자 수   |

이름 검색은 입력된 문자열이 환자 이름에 포함되는 환자를 조회하는 부분 일치 방식으로 처리합니다.

`min_age`와 `max_age`를 모두 전달하면 해당 범위에 포함되는 환자를 조회합니다. `min_age`는 `max_age`보다 클 수 없습니다.

#### 요청 예시

```http
GET /api/v1/patients/?name=김&gender=M&min_age=60&max_age=80&page=1&size=20
Authorization: Bearer <access_token>
```

### 응답(Response)

#### 성공

* `200 OK`

```json
{
  "items": [
    {
      "id": 1,
      "name": "김환자",
      "age": 65,
      "gender": "M",
      "phone": "01012345678",
      "created_at": "2026-06-11T15:30:00",
      "updated_at": null
    }
  ],
  "page": 1,
  "size": 20,
  "total": 1
}
```

#### 응답 필드

| 필드명                | 타입               | 설명                       |
| ------------------ | ---------------- | ------------------------ |
| items              | array            | 조회된 환자 목록                |
| items[].id         | integer          | 환자 고유 ID                 |
| items[].name       | string           | 환자 이름                    |
| items[].age        | integer          | 환자 나이                    |
| items[].gender     | string 또는 null   | 환자 성별                    |
| items[].phone      | string           | 환자 연락처                   |
| items[].created_at | datetime         | 환자 정보 등록 일시              |
| items[].updated_at | datetime 또는 null | 환자 정보 수정 일시              |
| page               | integer          | 현재 페이지 번호                |
| size               | integer          | 페이지당 조회 개수               |
| total              | integer          | 검색 및 필터 조건에 해당하는 전체 환자 수 |

검색 결과가 없는 경우에도 `200 OK`를 반환하며, `items`는 빈 배열이고 `total`은 0입니다.

```json
{
  "items": [],
  "page": 1,
  "size": 20,
  "total": 0
}
```

#### 실패

* `401 Unauthorized`: 인증 토큰이 없거나 유효하지 않은 경우
* `403 Forbidden`: 환자 목록 조회 권한이 없는 경우
* `422 Unprocessable Entity`: 성별, 나이 또는 페이지 값의 형식이 올바르지 않은 경우

```json
{
  "detail": "최소 나이는 최대 나이보다 클 수 없습니다."
}
```

---

## 3. 환자 상세 조회 API

| 항목              | 내용                                                 |
| --------------- | -------------------------------------------------- |
| 요구사항 ID         | `REQ-PTNT-003`                                     |
| API 이름          | 환자 상세 조회 API                                       |
| 설명              | 로그인한 사내 사용자가 환자 고유 ID를 기준으로 특정 환자의 상세 정보를 조회하는 API |
| 엔드포인트(Endpoint) | `/api/v1/patients/{patient_id}/`                   |
| 메서드(Method)     | `GET`                                              |
| 인증 필요 여부        | Y                                                  |
| 허용 권한           | `staff`, `admin`                                   |

### 요청(Request)

#### Headers

| Key           | Value                   | 설명         |
| ------------- | ----------------------- | ---------- |
| Authorization | `Bearer <access_token>` | JWT 액세스 토큰 |

#### Path Parameters

| 파라미터명      | 타입      | 필수 (Y/N) | 설명            |
| ---------- | ------- | -------- | ------------- |
| patient_id | integer | Y        | 조회할 환자의 고유 ID |

#### 요청 예시

```http
GET /api/v1/patients/1/
Authorization: Bearer <access_token>
```

### 응답(Response)

#### 성공

* `200 OK`

```json
{
  "id": 1,
  "name": "김환자",
  "age": 65,
  "gender": "M",
  "phone": "01012345678"
}
```

#### 응답 필드

| 필드명    | 타입             | 설명       |
| ------ | -------------- | -------- |
| id     | integer        | 환자 고유 ID |
| name   | string         | 환자 이름    |
| age    | integer        | 환자 나이    |
| gender | string 또는 null | 환자 성별    |
| phone  | string         | 환자 연락처   |

#### 실패

* `401 Unauthorized`: 인증 토큰이 없거나 유효하지 않은 경우
* `403 Forbidden`: 환자 상세 조회 권한이 없는 경우
* `404 Not Found`: 해당 `patient_id`의 환자가 존재하지 않는 경우
* `422 Unprocessable Entity`: `patient_id`가 정수 형식이 아닌 경우

```json
{
  "detail": "환자 정보를 찾을 수 없습니다."
}
```

---

## 4. 환자 정보 수정 API

| 항목              | 내용                                   |
| --------------- | ------------------------------------ |
| 요구사항 ID         | `REQ-PTNT-004`                       |
| API 이름          | 환자 정보 수정 API                         |
| 설명              | 로그인한 사내 사용자가 환자의 이름 또는 연락처를 수정하는 API |
| 엔드포인트(Endpoint) | `/api/v1/patients/{patient_id}/`     |
| 메서드(Method)     | `PATCH`                              |
| 인증 필요 여부        | Y                                    |
| 허용 권한           | `staff`, `admin`                     |

### 요청(Request)

#### Headers

| Key           | Value                   | 설명         |
| ------------- | ----------------------- | ---------- |
| Authorization | `Bearer <access_token>` | JWT 액세스 토큰 |
| Content-Type  | `application/json`      | 요청 데이터 형식  |

#### Path Parameters

| 파라미터명      | 타입      | 필수 (Y/N) | 설명            |
| ---------- | ------- | -------- | ------------- |
| patient_id | integer | Y        | 수정할 환자의 고유 ID |

#### 본문 예시

```json
{
  "name": "김수정",
  "phone": "01098765432"
}
```

#### 본문 필드

| 파라미터명 | 타입     | 필수 (Y/N) | 설명                           |
| ----- | ------ | -------- | ---------------------------- |
| name  | string | N        | 수정할 환자 이름, 최대 30자            |
| phone | string | N        | 수정할 국내 휴대폰 번호, 하이픈을 제외한 11자리 |

`name`과 `phone` 중 하나 이상의 필드를 전달해야 합니다.

요구사항에 따라 환자의 나이와 성별은 이 API에서 수정할 수 없습니다.

#### 요청 예시

```http
PATCH /api/v1/patients/1/
Authorization: Bearer <access_token>
Content-Type: application/json
```

### 응답(Response)

#### 성공

* `200 OK`

```json
{
  "id": 1,
  "name": "김수정",
  "age": 65,
  "gender": "M",
  "phone": "01098765432",
  "created_at": "2026-06-11T15:30:00",
  "updated_at": "2026-06-11T17:00:00"
}
```

#### 응답 필드

| 필드명        | 타입             | 설명          |
| ---------- | -------------- | ----------- |
| id         | integer        | 환자 고유 ID    |
| name       | string         | 수정된 환자 이름   |
| age        | integer        | 환자 나이       |
| gender     | string 또는 null | 환자 성별       |
| phone      | string         | 수정된 환자 연락처  |
| created_at | datetime       | 환자 정보 등록 일시 |
| updated_at | datetime       | 환자 정보 수정 일시 |

#### 실패

* `401 Unauthorized`: 인증 토큰이 없거나 유효하지 않은 경우
* `403 Forbidden`: 환자 정보 수정 권한이 없는 경우
* `404 Not Found`: 해당 `patient_id`의 환자가 존재하지 않는 경우
* `422 Unprocessable Entity`: 수정할 필드가 없거나 입력값 형식이 올바르지 않은 경우

```json
{
  "detail": "수정할 이름 또는 연락처를 입력해야 합니다."
}
```

---

## 5. 환자 정보 삭제 API

| 항목              | 내용                                                              |
| --------------- | --------------------------------------------------------------- |
| 요구사항 ID         | `REQ-PTNT-005`                                                  |
| API 이름          | 환자 정보 삭제 API                                                    |
| 설명              | 로그인한 사내 사용자가 특정 환자와 해당 환자에 연결된 진료기록 및 X-ray 이미지 정보를 영구 삭제하는 API |
| 엔드포인트(Endpoint) | `/api/v1/patients/{patient_id}/`                                |
| 메서드(Method)     | `DELETE`                                                        |
| 인증 필요 여부        | Y                                                               |
| 허용 권한           | `staff`, `admin`                                                |

### 요청(Request)

#### Headers

| Key           | Value                   | 설명         |
| ------------- | ----------------------- | ---------- |
| Authorization | `Bearer <access_token>` | JWT 액세스 토큰 |

#### Path Parameters

| 파라미터명      | 타입      | 필수 (Y/N) | 설명            |
| ---------- | ------- | -------- | ------------- |
| patient_id | integer | Y        | 삭제할 환자의 고유 ID |

#### 요청 예시

```http
DELETE /api/v1/patients/1/
Authorization: Bearer <access_token>
```

환자 삭제 요청 전 클라이언트 화면에서는 다음 내용을 안내하는 확인 팝업을 표시합니다.

```text
환자를 삭제하면 해당 환자의 진료기록 및 X-ray 이미지도 함께 영구 삭제됩니다.
삭제 후에는 복구할 수 없습니다. 삭제하시겠습니까?
```

팝업 표시는 프론트엔드의 책임이며, 실제 삭제 처리와 권한 검증은 서버에서 수행합니다.

### 삭제 처리 범위

환자 삭제 시 다음 데이터를 함께 삭제합니다.

| 삭제 대상           | 처리 방식                                      |
| --------------- | ------------------------------------------ |
| 환자 정보           | `patients` 테이블의 대상 환자 삭제                   |
| 진료기록            | 대상 환자와 연결된 `medical_records` 데이터 삭제        |
| X-ray 이미지 정보    | 삭제된 진료기록과 연결된 `xray_images` 데이터 삭제         |
| AI 분석 결과        | 삭제된 진료기록과 연결된 `ai_analysis_results` 데이터 삭제 |
| 로컬 X-ray 이미지 파일 | DB에 저장된 이미지 경로를 기준으로 서버 로컬 저장소에서 파일 삭제     |

ERD의 외래키 삭제 정책에 따라 환자가 삭제되면 관련 진료기록, X-ray 이미지 정보, AI 분석 결과가 연쇄 삭제됩니다.

로컬 저장소에 저장된 실제 X-ray 이미지 파일은 데이터베이스의 `ON DELETE CASCADE`만으로 삭제되지 않으므로, 서버의 파일 삭제 로직을 별도로 실행해야 합니다.

데이터베이스 레코드 삭제는 하나의 트랜잭션으로 처리하며, 오류가 발생하면 트랜잭션을 롤백합니다. 로컬 이미지 파일은 데이터베이스 트랜잭션의 적용 대상이 아니므로, 파일 삭제 실패 시 오류 기록과 재시도 또는 보상 처리 절차가 필요합니다.


### 응답(Response)

#### 성공

* `204 No Content`
* 삭제 성공 시 응답 본문을 반환하지 않습니다.

#### 실패

* `401 Unauthorized`: 인증 토큰이 없거나 유효하지 않은 경우
* `403 Forbidden`: 환자 정보 삭제 권한이 없는 경우
* `404 Not Found`: 해당 `patient_id`의 환자가 존재하지 않는 경우
* `500 Internal Server Error`: 관련 데이터 또는 이미지 파일 삭제 중 서버 오류가 발생한 경우

```json
{
  "detail": "환자 정보를 찾을 수 없습니다."
}
```

---

## 6. 진료기록 등록 API

| 항목              | 내용                                                  |
| --------------- | --------------------------------------------------- |
| 요구사항 ID         | `REQ-MDR-001`                                       |
| API 이름          | 진료기록 등록 API                                         |
| 설명              | 의료인 권한을 가진 사용자가 특정 환자의 진료정보와 흉부 X-ray 이미지를 등록하는 API |
| 엔드포인트(Endpoint) | `/api/v1/patients/{patient_id}/medical-records/`    |
| 메서드(Method)     | `POST`                                              |
| 인증 필요 여부        | Y                                                   |
| 허용 권한           | 의료 부서 소속의 `staff`, `admin`                          |
| 요청 형식           | `multipart/form-data`                               |

### 요청(Request)

#### Headers

| Key           | Value                   | 설명                          |
| ------------- | ----------------------- | --------------------------- |
| Authorization | `Bearer <access_token>` | JWT 액세스 토큰                  |
| Content-Type  | `multipart/form-data`   | 텍스트 데이터와 이미지 파일을 함께 전송하는 형식 |

`multipart/form-data` 요청의 `Content-Type` 경계값인 `boundary`는 클라이언트가 자동으로 생성하도록 합니다.

#### Path Parameters

| 파라미터명      | 타입      | 필수 (Y/N) | 설명                  |
| ---------- | ------- | -------- | ------------------- |
| patient_id | integer | Y        | 진료기록을 등록할 환자의 고유 ID |

#### Form Data

| 파라미터명             | 타입       | 필수 (Y/N) | 설명                          |
| ----------------- | -------- | -------- | --------------------------- |
| chart_number      | string   | Y        | 진료 차트 번호, 최대 50자이며 고유값      |
| symptoms          | string   | Y        | 환자의 증상 및 진료 내용              |
| xray_image        | file     | Y        | 촬영된 흉부 X-ray 이미지 파일         |
| shooting_datetime | datetime | Y        | 흉부 X-ray 촬영 일시, ISO 8601 형식 |

환자 고유 ID는 URL의 `patient_id`로 전달합니다.

X-ray 이미지를 업로드한 사용자 정보인 `uploader_id`는 요청 본문으로 받지 않습니다. 서버는 JWT 액세스 토큰으로 인증된 사용자의 ID를 추출하여 저장합니다.

#### 요청 예시

```http
POST /api/v1/patients/1/medical-records/
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

```text
chart_number=CHART-2026-0001
symptoms=발열과 기침이 지속되며 호흡곤란 증상이 있음
shooting_datetime=2026-06-11T14:30:00
xray_image=chest_xray_001.jpg
```

### 이미지 저장 처리

업로드된 X-ray 이미지는 서버가 실행되는 환경의 로컬 저장소에 저장합니다.

데이터베이스의 `xray_images.image_url`에는 이미지 파일 자체가 아니라 저장된 파일에 접근하기 위한 경로를 저장합니다.

파일명 충돌과 경로 조작을 방지하기 위해 서버에서 UUID 등을 이용하여 새로운 파일명을 생성합니다.

```text
원본 파일명: chest_xray_001.jpg
저장 파일명: 550e8400-e29b-41d4-a716-446655440000.jpg
저장 경로: media/xrays/550e8400-e29b-41d4-a716-446655440000.jpg
```

허용할 이미지 확장자와 최대 파일 크기는 별도의 운영 정책으로 확정해야 합니다.

### 등록 처리 순서

서버는 다음 순서로 진료기록을 등록합니다.

1. 사용자 인증 및 의료인 권한을 확인합니다.
2. `patient_id`에 해당하는 환자가 존재하는지 확인합니다.
3. `chart_number`가 이미 등록되어 있는지 확인합니다.
4. 업로드된 파일이 허용된 이미지 형식인지 확인합니다.
5. X-ray 이미지를 로컬 저장소에 저장합니다.
6. `medical_records` 테이블에 진료기록을 저장합니다.
7. `xray_images` 테이블에 이미지 경로, 촬영 일시, 업로더 정보를 저장합니다.
8. 데이터베이스 처리가 성공하면 트랜잭션을 커밋합니다.

이미지 파일 저장 후 데이터베이스 등록이 실패하면, 데이터 불일치를 방지하기 위해 저장된 이미지 파일을 삭제하는 보상 처리를 수행합니다.

### 응답(Response)

#### 성공

* `201 Created`

```json
{
  "id": 1,
  "patient_id": 1,
  "chart_number": "CHART-2026-0001",
  "symptoms": "발열과 기침이 지속되며 호흡곤란 증상이 있음",
  "created_at": "2026-06-11T15:30:00",
  "updated_at": null,
  "xray_image": {
    "id": 1,
    "image_url": "/media/xrays/550e8400-e29b-41d4-a716-446655440000.jpg",
    "shooting_datetime": "2026-06-11T14:30:00",
    "created_at": "2026-06-11T15:30:00"
  }
}
```

#### 응답 필드

| 필드명                          | 타입               | 설명                 |
| ---------------------------- | ---------------- | ------------------ |
| id                           | integer          | 진료기록 고유 ID         |
| patient_id                   | integer          | 진료기록과 연결된 환자 고유 ID |
| chart_number                 | string           | 진료 차트 번호           |
| symptoms                     | string           | 환자의 증상 및 진료 내용     |
| created_at                   | datetime         | 진료기록 등록 일시         |
| updated_at                   | datetime 또는 null | 진료기록 수정 일시         |
| xray_image                   | object           | 등록된 X-ray 이미지 정보   |
| xray_image.id                | integer          | X-ray 이미지 고유 ID    |
| xray_image.image_url         | string           | X-ray 이미지 접근 경로    |
| xray_image.shooting_datetime | datetime         | X-ray 촬영 일시        |
| xray_image.created_at        | datetime         | X-ray 이미지 등록 일시    |

#### 실패

* `400 Bad Request`: 업로드 파일이 허용된 이미지 형식이나 용량 기준을 충족하지 않는 경우
* `401 Unauthorized`: 인증 토큰이 없거나 유효하지 않은 경우
* `403 Forbidden`: 진료기록 등록 권한이 없는 경우
* `404 Not Found`: 해당 `patient_id`의 환자가 존재하지 않는 경우
* `409 Conflict`: 동일한 진료 차트 번호가 이미 존재하는 경우
* `422 Unprocessable Entity`: 필수 입력값이 누락되었거나 형식이 올바르지 않은 경우
* `500 Internal Server Error`: 이미지 저장 또는 데이터베이스 등록 중 오류가 발생한 경우

```json
{
  "detail": "이미 등록된 진료 차트 번호입니다."
}
```

---

## 7. 환자별 진료기록 목록 조회 API

| 항목              | 내용                                               |
| --------------- | ------------------------------------------------ |
| 요구사항 ID         | `REQ-MDR-002`                                    |
| API 이름          | 환자별 진료기록 목록 조회 API                               |
| 설명              | 로그인한 사내 사용자가 특정 환자에게 등록된 진료기록 목록을 조회하는 API       |
| 엔드포인트(Endpoint) | `/api/v1/patients/{patient_id}/medical-records/` |
| 메서드(Method)     | `GET`                                            |
| 인증 필요 여부        | Y                                                |
| 허용 권한           | `staff`, `admin`                                 |

### 요청(Request)

#### Headers

| Key           | Value                   | 설명         |
| ------------- | ----------------------- | ---------- |
| Authorization | `Bearer <access_token>` | JWT 액세스 토큰 |

#### Path Parameters

| 파라미터명      | 타입      | 필수 (Y/N) | 설명                     |
| ---------- | ------- | -------- | ---------------------- |
| patient_id | integer | Y        | 진료기록 목록을 조회할 환자의 고유 ID |

#### Query Parameters

| 파라미터명 | 타입      | 필수 (Y/N) | 기본값 | 설명                |
| ----- | ------- | -------- | --- | ----------------- |
| page  | integer | N        | 1   | 조회할 페이지 번호        |
| size  | integer | N        | 20  | 한 페이지에 조회할 진료기록 수 |

#### 요청 예시

```http
GET /api/v1/patients/1/medical-records/?page=1&size=20
Authorization: Bearer <access_token>
```

### 증상 요약 처리

목록에서는 진료기록의 전체 증상 내용이 아니라 요약된 내용을 반환합니다.

증상 내용이 100자 이하이면 원문을 그대로 반환합니다.

증상 내용이 100자를 초과하면 앞의 100자까지만 반환하고, 뒤에 생략 기호 `...`를 추가합니다.

```text
원문 길이 100자 이하: 발열과 기침이 지속됨
응답값: 발열과 기침이 지속됨
```

```text
원문 길이 100자 초과: 앞의 100자 + ...
```

상세 조회 API에서는 축약하지 않은 전체 증상 내용을 반환합니다.

### 응답(Response)

#### 성공

* `200 OK`

```json
{
  "items": [
    {
      "id": 1,
      "chart_number": "CHART-2026-0001",
      "symptoms": "발열과 기침이 지속되며 호흡곤란 증상이 있음",
      "created_at": "2026-06-11T15:30:00"
    },
    {
      "id": 2,
      "chart_number": "CHART-2026-0002",
      "symptoms": "증상 내용이 100자를 초과하는 경우 앞의 100자까지만 반환하고 나머지 내용은 목록 응답에서 생략하여 표시합니다...",
      "created_at": "2026-06-12T10:20:00"
    }
  ],
  "page": 1,
  "size": 20,
  "total": 2
}
```

#### 응답 필드

| 필드명                  | 타입       | 설명                       |
| -------------------- | -------- | ------------------------ |
| items                | array    | 해당 환자에게 등록된 진료기록 목록      |
| items[].id           | integer  | 진료기록 고유 ID               |
| items[].chart_number | string   | 진료 차트 번호                 |
| items[].symptoms     | string   | 증상 내용이며, 100자 초과 시 축약된 값 |
| items[].created_at   | datetime | 진료기록 등록 일시               |
| page                 | integer  | 현재 페이지 번호                |
| size                 | integer  | 페이지당 조회 개수               |
| total                | integer  | 해당 환자에게 등록된 전체 진료기록 수    |

진료기록이 없는 경우에도 `200 OK`를 반환하며, `items`는 빈 배열이고 `total`은 0입니다.

```json
{
  "items": [],
  "page": 1,
  "size": 20,
  "total": 0
}
```

#### 실패

* `401 Unauthorized`: 인증 토큰이 없거나 유효하지 않은 경우
* `403 Forbidden`: 진료기록 목록 조회 권한이 없는 경우
* `404 Not Found`: 해당 `patient_id`의 환자가 존재하지 않는 경우
* `422 Unprocessable Entity`: `patient_id`, `page` 또는 `size`의 형식이나 범위가 올바르지 않은 경우

```json
{
  "detail": "환자 정보를 찾을 수 없습니다."
}
```

---

## 8. 진료기록 상세 조회 API

| 항목              | 내용                                                           |
| --------------- | ------------------------------------------------------------ |
| 요구사항 ID         | `REQ-MDR-003`                                                |
| API 이름          | 진료기록 상세 조회 API                                               |
| 설명              | 로그인한 사내 사용자가 특정 환자의 진료기록과 흉부 X-ray 이미지 정보를 상세 조회하는 API       |
| 엔드포인트(Endpoint) | `/api/v1/patients/{patient_id}/medical-records/{record_id}/` |
| 메서드(Method)     | `GET`                                                        |
| 인증 필요 여부        | Y                                                            |
| 허용 권한           | `staff`, `admin`                                             |

### 요청(Request)

#### Headers

| Key           | Value                   | 설명         |
| ------------- | ----------------------- | ---------- |
| Authorization | `Bearer <access_token>` | JWT 액세스 토큰 |

#### Path Parameters

| 파라미터명      | 타입      | 필수 (Y/N) | 설명                 |
| ---------- | ------- | -------- | ------------------ |
| patient_id | integer | Y        | 진료기록이 속한 환자의 고유 ID |
| record_id  | integer | Y        | 조회할 진료기록의 고유 ID    |

#### 요청 예시

```http
GET /api/v1/patients/1/medical-records/1/
Authorization: Bearer <access_token>
```

서버는 `record_id`에 해당하는 진료기록이 URL의 `patient_id`에 속하는지 함께 확인합니다.

진료기록이 존재하더라도 해당 환자의 진료기록이 아니라면 다른 환자의 정보 노출을 방지하기 위해 `404 Not Found`를 반환합니다.

### 응답(Response)

#### 성공

* `200 OK`

```json
{
  "id": 1,
  "patient_id": 1,
  "chart_number": "CHART-2026-0001",
  "symptoms": "발열과 기침이 지속되며 호흡곤란 증상이 있어 흉부 X-ray 촬영을 시행함",
  "created_at": "2026-06-11T15:30:00",
  "updated_at": null,
  "xray_images": [
    {
      "id": 1,
      "image_url": "/media/xrays/550e8400-e29b-41d4-a716-446655440000.jpg",
      "shooting_datetime": "2026-06-11T14:30:00",
      "created_at": "2026-06-11T15:30:00"
    }
  ]
}
```

#### 응답 필드

| 필드명                             | 타입               | 설명                        |
| ------------------------------- | ---------------- | ------------------------- |
| id                              | integer          | 진료기록 고유 ID                |
| patient_id                      | integer          | 진료기록과 연결된 환자 고유 ID        |
| chart_number                    | string           | 진료 차트 번호                  |
| symptoms                        | string           | 축약하지 않은 전체 증상 및 진료 내용     |
| created_at                      | datetime         | 진료기록 등록 일시                |
| updated_at                      | datetime 또는 null | 진료기록 수정 일시                |
| xray_images                     | array            | 진료기록과 연결된 흉부 X-ray 이미지 목록 |
| xray_images[].id                | integer          | X-ray 이미지 고유 ID           |
| xray_images[].image_url         | string           | X-ray 이미지 접근 경로           |
| xray_images[].shooting_datetime | datetime         | X-ray 촬영 일시               |
| xray_images[].created_at        | datetime         | X-ray 이미지 등록 일시           |

진료기록에 연결된 X-ray 이미지가 없는 경우 `xray_images`는 빈 배열로 반환합니다.

```json
{
  "id": 1,
  "patient_id": 1,
  "chart_number": "CHART-2026-0001",
  "symptoms": "발열과 기침이 지속됨",
  "created_at": "2026-06-11T15:30:00",
  "updated_at": null,
  "xray_images": []
}
```

#### 실패

* `401 Unauthorized`: 인증 토큰이 없거나 유효하지 않은 경우
* `403 Forbidden`: 진료기록 상세 조회 권한이 없는 경우
* `404 Not Found`: 환자 또는 진료기록이 존재하지 않거나, 해당 진료기록이 URL의 환자에게 속하지 않는 경우
* `422 Unprocessable Entity`: `patient_id` 또는 `record_id`가 정수 형식이 아닌 경우

```json
{
  "detail": "진료기록을 찾을 수 없습니다."
}
```
