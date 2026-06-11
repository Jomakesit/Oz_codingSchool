from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.databases import async_get_db
from app.core.dependencies import get_current_user, require_admin
from app.models.enums import Department
from app.models.users import User
from app.schemas.user_schemas import (
    PasswordChangeRequest,
    RoleUpdateRequest,
    RoleUpdateResponse,
    UserDeleteRequest,
    UserListResponse,
    UserRegisterRequest,
    UserResponse,
    UserUpdateRequest,
)
from app.services.user_service import UserService

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.post("/register/", response_model=UserResponse, status_code=201)
async def register(
    data: UserRegisterRequest,
    db: AsyncSession = Depends(async_get_db),
):
    return await UserService(db).register(data)


@router.get("/", response_model=UserListResponse)
async def get_users(
    search: str | None = Query(None, description="이메일 또는 이름 검색"),
    department: Department | None = Query(None, description="부서 필터"),
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(async_get_db),
):
    count, users = await UserService(db).get_user_list(search=search, department=department)
    return {"count": count, "results": users}


# /me 관련 엔드포인트는 /{user_id} 형태보다 먼저 등록해야 라우팅 충돌이 없음
@router.get("/me/", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me/", response_model=UserResponse)
async def update_me(
    data: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(async_get_db),
):
    return await UserService(db).update_my_info(current_user, data)


@router.put("/me/password/")
async def change_password(
    data: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(async_get_db),
):
    await UserService(db).change_password(
        current_user, data.current_password, data.new_password
    )
    return {"detail": "비밀번호가 성공적으로 변경되었습니다."}


@router.delete("/me/", status_code=204)
async def delete_me(
    data: UserDeleteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(async_get_db),
):
    await UserService(db).delete_account(current_user, data.password)


@router.patch("/{user_id}/role/", response_model=RoleUpdateResponse)
async def update_role(
    user_id: int,
    data: RoleUpdateRequest,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(async_get_db),
):
    return await UserService(db).update_role(user_id, data.role)
