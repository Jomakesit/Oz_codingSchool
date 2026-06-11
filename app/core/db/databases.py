from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.core.config import settings

Base = declarative_base()

if settings.USE_SQLITE:
    # MySQL 없이 로컬 테스트용 SQLite (파일 기반)
    DATABASE_URL = "sqlite+aiosqlite:///./dev_test.db"
    async_engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False},
    )
else:
    DATABASE_PREFIX = "mysql+asyncmy://"
    DATABASE_URI = f"{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    DATABASE_URL = f"{DATABASE_PREFIX}{DATABASE_URI}"
    async_engine = create_async_engine(DATABASE_URL, echo=False, future=True)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine, autoflush=False, expire_on_commit=False
)


async def async_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as db:
        yield db
