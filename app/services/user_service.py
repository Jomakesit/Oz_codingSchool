from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.models.enums import Department, Role
from app.models.users import User
from app.repositories.user_repository import UserRepository
from app.schemas.user_schemas import UserRegisterRequest, UserUpdateRequest


class UserService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def register(self, data: UserRegisterRequest) -> User:
        if await self.repo.get_by_email(data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 사용 중인 이메일입니다.",
            )
        if await self.repo.get_by_phone(data.phone_number):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 사용 중인 휴대폰 번호입니다.",
            )

        user = User(
            email=data.email,
            hashed_password=hash_password(data.password),
            name=data.name,
            department=data.department,
            gender=data.gender,
            phone_number=data.phone_number,
            role=Role.PENDING,
        )
        return await self.repo.create(user)

    async def get_user_list(
        self,
        search: str | None,
        department: Department | None,
    ) -> tuple[int, list[User]]:
        users = await self.repo.get_all(search=search, department=department)
        return len(users), users

    async def update_role(self, user_id: int, role: Role) -> User:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 사용자를 찾을 수 없습니다.",
            )
        return await self.repo.update(user, {"role": role})

    async def update_my_info(self, user: User, data: UserUpdateRequest) -> User:
        fields = data.model_dump(exclude_unset=True)
        if not fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="수정 가능한 필드가 포함되어 있지 않습니다.",
            )
        return await self.repo.update(user, fields)

    async def change_password(
        self, user: User, current_password: str, new_password: str
    ) -> None:
        if not verify_password(current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="기존 비밀번호가 일치하지 않습니다.",
            )
        if current_password == new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="새 비밀번호가 기존 비밀번호와 동일합니다.",
            )
        await self.repo.update(user, {"hashed_password": hash_password(new_password)})

    async def delete_account(self, user: User, password: str) -> None:
        if not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="비밀번호가 일치하지 않습니다.",
            )
        await self.repo.delete(user)
