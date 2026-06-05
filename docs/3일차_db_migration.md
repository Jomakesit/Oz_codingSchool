아래 내용을 그대로 `docs/3일차_db_migration.md`에 붙여넣으면 됩니다.

````markdown
# 3일차 DB Migration

## 1. DB 모델 작성 기준

이번 작업에서는 제공된 ERD를 기준으로 SQLAlchemy ORM 모델과 Alembic 마이그레이션 파일을 작성하였다. 모델 파일은 `app/models/` 하위에 테이블 단위로 분리하였다.

작성한 모델 파일은 다음과 같다.

```text
app/models/enums.py
app/models/users.py
app/models/patients.py
app/models/medical_records.py
app/models/xray_images.py
app/models/ai_analysis_results.py
app/models/__init__.py
````

각 모델은 `app/core/db/databases.py`에 정의된 `Base`를 상속받아 작성하였다.

```python
from app.core.db.databases import Base
```

Alembic이 모델을 인식할 수 있도록 `app/models/__init__.py`에서 작성한 모델들을 import하였다.

```python
from app.models.users import User
from app.models.patients import Patient
from app.models.medical_records import MedicalRecord
from app.models.xray_images import XrayImage
from app.models.ai_analysis_results import AiAnalysisResult
```

## 2. 작성한 테이블 모델

### users

`users` 테이블은 서비스 사용자의 계정 정보를 저장한다.

주요 컬럼은 다음과 같다.

```text
id
email
hashed_password
name
phone_number
gender
department
role
is_active
created_at
updated_at
```

`email`과 `phone_number`는 unique 제약을 가진다. `gender`, `department`, `role`은 Enum으로 관리한다. 비밀번호는 평문이 아니라 해시된 값인 `hashed_password`로 저장하는 구조이다.

### patients

`patients` 테이블은 환자 정보를 저장한다.

주요 컬럼은 다음과 같다.

```text
id
name
age
gender
phone
created_at
updated_at
```

환자 이름, 나이, 성별, 연락처, 등록일시와 수정일시를 관리한다. 제공 ERD 기준으로 `gender`는 nullable로 정의되어 있다.

### medical_records

`medical_records` 테이블은 환자의 진료 기록을 저장한다.

주요 컬럼은 다음과 같다.

```text
id
patient_id
chart_number
symptoms
created_at
updated_at
```

`patient_id`는 `patients.id`를 참조한다. 제공 ERD 기준으로 환자 정보가 삭제되면 해당 환자의 진료 기록도 함께 삭제되도록 `ON DELETE CASCADE`를 적용하였다.

### xray_images

`xray_images` 테이블은 진료 기록과 연결된 X-ray 이미지 정보를 저장한다.

주요 컬럼은 다음과 같다.

```text
id
record_id
uploader_id
image_url
shooting_datetime
created_at
```

`record_id`는 `medical_records.id`를 참조한다. 제공 ERD 기준으로 진료 기록이 삭제되면 연결된 X-ray 이미지도 함께 삭제되도록 `ON DELETE CASCADE`를 적용하였다.

`uploader_id`는 X-ray 이미지를 업로드한 사용자를 나타내며 `users.id`를 참조한다.

### ai_analysis_results

`ai_analysis_results` 테이블은 AI 폐렴 분석 결과를 저장한다.

주요 컬럼은 다음과 같다.

```text
id
record_id
is_pneumonia
confidence
heatmap_url
ai_model
created_at
updated_at
```

`record_id`는 `medical_records.id`를 참조한다. 진료 기록이 삭제되면 연결된 AI 분석 결과도 함께 삭제되도록 `ON DELETE CASCADE`를 적용하였다.

## 3. ERD 구현 중 조정 사항

제공 ERD를 기준으로 모델을 작성하였으나, 실제 MySQL 마이그레이션 적용 과정에서 `xray_images.uploader_id`와 관련하여 두 가지 제약 충돌이 확인되었다.

### 3-1. `NOT NULL`과 `ON DELETE SET NULL` 충돌

제공 ERD에서는 `xray_images.uploader_id`가 `not null`로 정의되어 있다.

```text
uploader_id bigint [not null, note: "X-ray 이미지를 업로드한 유저의 id"]
```

그러나 FK 관계에서는 다음과 같이 `users.id` 삭제 시 `SET NULL` 정책을 사용한다.

```text
Ref: xray_images.uploader_id > users.id [delete: set null]
```

`ON DELETE SET NULL`은 참조 대상 row가 삭제될 때 FK 컬럼 값을 `NULL`로 변경하는 정책이다. 따라서 FK 컬럼이 `NOT NULL`이면 MySQL에서 해당 제약 조건을 생성할 수 없다.

실제 마이그레이션 적용 과정에서도 다음 유형의 오류가 발생하였다.

```text
Column 'uploader_id' cannot be NOT NULL: needed in a foreign key constraint SET NULL
```

따라서 제공 ERD의 삭제 정책인 `SET NULL`을 실제 DB에서 동작 가능하게 하기 위해 `xray_images.uploader_id`를 `nullable=True`로 조정하였다.

### 3-2. FK 컬럼 타입 불일치

제공 ERD에서는 `users.id`가 `integer`로 정의되어 있고, `xray_images.uploader_id`는 `bigint`로 정의되어 있다.

```text
users.id integer
xray_images.uploader_id bigint
```

그러나 `xray_images.uploader_id`는 `users.id`를 참조하는 FK 컬럼이므로, 실제 MySQL에서는 참조 컬럼과 참조 대상 컬럼의 타입 정합성이 맞아야 한다.

마이그레이션 적용 과정에서 다음 유형의 오류가 발생하였다.

```text
Referencing column 'uploader_id' and referenced column 'id' in foreign key constraint are incompatible.
```

따라서 참조 대상인 `users.id`의 타입에 맞추기 위해 `xray_images.uploader_id`를 `Integer`로 조정하였다.

최종 구현에서는 다음과 같이 작성하였다.

```python
uploader_id = Column(
    Integer,
    ForeignKey("users.id", ondelete="SET NULL"),
    nullable=True,
    comment="X-ray 이미지를 업로드한 유저의 id"
)
```

이 조정은 제공 ERD의 FK 삭제 정책인 `SET NULL`을 유지하면서 실제 MySQL 제약 조건을 통과시키기 위한 최소 수정이다.

## 4. Alembic 마이그레이션 생성

모델 import가 정상적으로 되는지 먼저 확인하였다.

```bash
python3 -c "from app import models; print('models import ok')"
```

실행 결과는 다음과 같다.

```text
models import ok
```

이후 Alembic autogenerate 명령어로 마이그레이션 파일을 생성하였다.

```bash
python3 -m alembic revision --autogenerate -m "create db models"
```

생성된 마이그레이션 파일은 다음 위치에 생성되었다.

```text
alembic/versions/d1e1cf851d9f_create_db_models.py
```

Alembic은 다음 테이블들이 새로 추가된 것으로 감지하였다.

```text
patients
users
medical_records
ai_analysis_results
xray_images
```

## 5. 마이그레이션 적용

생성된 마이그레이션 파일을 DB에 적용하기 위해 다음 명령어를 실행하였다.

```bash
python3 -m alembic upgrade head
```

초기 적용 과정에서는 `xray_images.uploader_id`의 `NOT NULL`과 `ON DELETE SET NULL` 충돌, 그리고 `users.id`와 `xray_images.uploader_id`의 타입 불일치로 인해 오류가 발생하였다.

해당 문제를 반영하여 `xray_images.uploader_id`를 `Integer`, `nullable=True`로 조정한 뒤 다시 마이그레이션을 적용하였다.

최종적으로 다음 명령어가 정상 실행되었다.

```bash
python3 -m alembic upgrade head
```

실행 로그는 다음과 같다.

```text
INFO  [alembic.runtime.migration] Context impl MySQLImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> d1e1cf851d9f, create db models
```

오류 없이 프롬프트로 돌아왔으므로 마이그레이션 적용은 정상 완료된 것으로 판단하였다.

## 6. DB 적용 결과 확인

MySQL에 접속하여 테이블 생성 여부를 확인하였다.

```bash
mysql -u ozcoding -p ai_health
```

접속 후 다음 SQL을 실행하였다.

```sql
SHOW TABLES;
```

확인 결과는 다음과 같다.

```text
+---------------------+
| Tables_in_ai_health |
+---------------------+
| ai_analysis_results |
| alembic_version     |
| medical_records     |
| patients            |
| users               |
| xray_images         |
+---------------------+
```

따라서 ERD 기반으로 작성한 주요 테이블 5개와 Alembic 버전 관리 테이블이 생성되었다.

추가로 `xray_images` 테이블 구조를 확인하였다.

```sql
DESC xray_images;
```

확인 결과는 다음과 같다.

```text
+-------------------+---------------+------+-----+---------+-------------------+
| Field             | Type          | Null | Key | Default | Extra             |
+-------------------+---------------+------+-----+---------+-------------------+
| id                | bigint        | NO   | PRI | NULL    | auto_increment    |
| record_id         | bigint        | NO   | MUL | NULL    |                   |
| uploader_id       | int           | YES  | MUL | NULL    |                   |
| image_url         | varchar(2048) | NO   |     | NULL    |                   |
| shooting_datetime | datetime      | NO   |     | NULL    |                   |
| created_at        | datetime      | NO   |     | now()   | DEFAULT_GENERATED |
+-------------------+---------------+------+-----+---------+-------------------+
```

`uploader_id`는 `int`, `NULL 허용`으로 적용되었다. 이는 `users.id`와 FK 타입 정합성을 맞추고, `ON DELETE SET NULL` 정책을 적용하기 위한 조정 결과이다.

## 7. 최종 결과

최종적으로 다음 작업을 완료하였다.

```text
SQLAlchemy 모델 파일 작성
app/models/__init__.py 모델 import 연결
Alembic 마이그레이션 파일 생성
MySQL DB에 마이그레이션 적용
DB 테이블 생성 확인
ERD와 실제 DB 제약 조건의 충돌 지점 문서화
```

생성된 주요 테이블은 다음과 같다.

```text
users
patients
medical_records
xray_images
ai_analysis_results
```

이번 작업에서는 제공 ERD를 기준으로 구현하되, 실제 DB 제약 조건상 실행이 불가능한 `xray_images.uploader_id` 부분은 `Integer`, `nullable=True`로 조정하였다. 이 조정은 `users.id`와의 FK 타입 정합성을 맞추고, `ON DELETE SET NULL` 정책을 실제 DB에서 적용하기 위한 것이다.

```
```
