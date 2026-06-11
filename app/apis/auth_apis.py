from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db.databases import async_get_db
from app.core.dependencies import get_current_user
from app.models.users import User
from app.schemas.user_schemas import LoginResponse, TokenRefreshResponse, UserLoginRequest
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login/", response_model=LoginResponse)
async def login(
    data: UserLoginRequest,
    response: Response,
    db: AsyncSession = Depends(async_get_db),
):
    result = await AuthService(db).login(data.email, data.password)

    response.set_cookie(
        key="refresh_token",
        value=result["refresh_token"],
        httponly=True,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
        samesite="lax",
    )

    return {"access_token": result["access_token"], "user": result["user"]}


@router.post("/token/refresh/", response_model=TokenRefreshResponse)
async def refresh_token(
    refresh_token: str | None = Cookie(None),
    db: AsyncSession = Depends(async_get_db),
):
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="리프레시 토큰이 없습니다.",
        )
    access_token = await AuthService(db).refresh_access_token(refresh_token)
    return {"access_token": access_token}


@router.post("/logout/")
async def logout(
    response: Response,
    _: User = Depends(get_current_user),
):
    response.delete_cookie(key="refresh_token")
    return {"detail": "정상적으로 로그아웃 되었습니다."}
