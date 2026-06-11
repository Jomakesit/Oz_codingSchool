import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles

from app.core.config import settings
# from app.core.db.databases import Base, async_engine
from app.apis import auth_apis, patient_apis, practice_apis, user_apis

# ⭐️
from app.apis import auth_apis, practice_apis, user_apis


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.USE_SQLITE:
        # SQLite 모드에서는 서버 시작 시 테이블 자동 생성
        import app.models  # noqa: F401 — 모든 모델을 Base에 등록
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)
# ⭐️
app.include_router(practice_apis.router)
app.include_router(user_apis.router)
app.include_router(auth_apis.router)
#
app.include_router(patient_apis.router)

BASE_DIR = Path(__file__).resolve().parent.parent

# 만약 static, media 폴더가 존재하지 않으면 생성
if not (BASE_DIR / "static").exists(): 
    os.mkdir(BASE_DIR / "static")

if not (BASE_DIR / "media").exists(): 
    os.mkdir(BASE_DIR / "media")

# 'static' 폴더를 '/static' 경로로 마운트 (CSS, JS 파일 서빙용)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# 'media' 폴더를 '/media' 경로로 마운트 (사용자 업로드 파일 서빙용)
app.mount("/media", StaticFiles(directory=BASE_DIR / "media"), name="media")

@app.get(
        path="/healthcheck", 
        status_code=200, 
        include_in_schema=False
        ) 
async def healthcheck(): 
    return {"status": "ok"}

@app.get("/", include_in_schema=False) 
async def index(): 
    return FileResponse(BASE_DIR / "static" / "index.html")

@app.get("/{path:path}", include_in_schema=False) 
async def catch_all(path: str):
    # API나 정적 파일 경로는 제외 (FastAPI가 먼저 매칭하지 못한 경우에만 실행됨)
    if ( 
        path.startswith("api/v1")
        or path.startswith("practice_api/") 
        or path.startswith("static/") 
        or path.startswith("media/") 
    ): 
        from fastapi import HTTPException

        raise HTTPException(status_code=404)
    return FileResponse(BASE_DIR / "static" / "index.html")