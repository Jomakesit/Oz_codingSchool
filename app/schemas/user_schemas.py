from pydantic import BaseModel
from app.models.enums import Department, Gender, Role


# ── 요청(Request) 스키마 ──────────────────────────────────────────

class UserRegisterRequest(BaseModel):
    email: str
    password: str
    name: str
    department: Department
    gender: Gender
    phone_number: str


class UserLoginRequest(BaseModel):
    email: str
    password: str


class UserUpdateRequest(BaseModel):
    department: Department | None = None
    phone_number: str | None = None


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str


class RoleUpdateRequest(BaseModel):
    role: Role


class UserDeleteRequest(BaseModel):
    password: str


# ── 응답(Response) 스키마 ─────────────────────────────────────────

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    department: Department
    gender: Gender
    phone_number: str
    role: Role

    model_config = {"from_attributes": True}


class UserBasicResponse(BaseModel):
    """로그인 응답의 user 필드용 (id, email, name, role만 포함)"""
    id: int
    email: str
    name: str
    role: Role

    model_config = {"from_attributes": True}


class UserListItem(BaseModel):
    id: int
    email: str
    name: str
    department: Department
    gender: Gender
    phone_number: str
    is_active: bool
    role: Role

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    count: int
    results: list[UserListItem]


class RoleUpdateResponse(BaseModel):
    id: int
    email: str
    name: str
    role: Role

    model_config = {"from_attributes": True}


class LoginResponse(BaseModel):
    access_token: str
    user: UserBasicResponse


class TokenRefreshResponse(BaseModel):
    access_token: str
