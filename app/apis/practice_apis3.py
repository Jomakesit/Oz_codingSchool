import re
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator


user_list = [
	{
		"id": 1,
		"name": "홍길동",
		"age": 24,
		"email": "gildong24@example.com",
		"password": "Password1234!!"
	},
	{
		"id": 2,
		"name": "장문복",
		"age": 21,
		"email": "moonluck12@example.com",
		"password": "Check1321!"
	},
	{
		"id": 3,
		"name": "임우진",
		"age": 31,
		"email": "limousine33@example.com",
		"password": "lwsPAssword12@"
	}
]

# 라우터 생성 시 팀원과 동일하게 prefix 추가
router = APIRouter(
    prefix="/practice_api",
    tags=["practice_api"]
)

# 회원 정보 수정 데이터 검증 스키마
class UserUpdateSchema(BaseModel):
    age: Optional[int] = Field(None, ge=14)
    email: Optional[str] = Field(None, max_length=30)
    password: Optional[str] = Field(None, min_length=8, max_length=20)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        if v is not None:
            email_regex = r"^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$"
            if not re.match(email_regex, v):
                raise ValueError("올바른 이메일 형식이 아닙니다.")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if v is not None:
            if not any(c.isupper() for c in v):
                raise ValueError("비밀번호에 대문자가 최소 1개 이상 포함되어야 합니다.")
            if not any(c.islower() for c in v):
                raise ValueError("비밀번호에 소문자가 최소 1개 이상 포함되어야 합니다.")
            special_chars = "!@#$%^&*(),.?\":{}|<>"
            if not any(c in special_chars for c in v):
                raise ValueError("비밀번호에 특수문자가 최소 1개 이상 포함되어야 합니다.")
        return v

# 회원 정보 수정 API (PATCH)
# 데코레이터 경로에 /users 추가 (PATCH 메서드 유지)
@router.patch("/users/{user_id}")
def update_user(user_id: int, data: UserUpdateSchema):
    update_data = data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="수정할 항목을 입력해주세요.")

    for user in user_list:
        if user["id"] == user_id:
            user.update(update_data)
            return {"message": "성공적으로 수정되었습니다.", "user": user}

    raise HTTPException(status_code=404, detail="User not found")