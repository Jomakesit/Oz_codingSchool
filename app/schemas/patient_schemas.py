from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.models.enums import Gender


class PatientCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=30)
    age: int = Field(..., ge=0)
    gender: Gender
    phone: str = Field(..., min_length=11, max_length=11)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        if not value.isdigit():
            raise ValueError("휴대폰 번호는 숫자만 입력해야 합니다.")
        if not value.startswith("010"):
            raise ValueError("휴대폰 번호는 010으로 시작해야 합니다.")
        return value


class PatientResponse(BaseModel):
    id: int
    name: str
    age: int
    gender: Gender | None
    phone: str
    created_at: datetime
    updated_at: datetime | None

    model_config = {"from_attributes": True}
