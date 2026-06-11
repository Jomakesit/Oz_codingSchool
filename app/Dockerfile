FROM python:3.13-slim

# uv가 가상환경 없이 시스템 Python을 직접 사용하도록 설정
ENV UV_SYSTEM_PYTHON=1

WORKDIR /code

# uv 공식 이미지에서 바이너리만 복사 (별도 설치 불필요)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 의존성 파일만 먼저 복사 → 소스 코드 변경 시 이 레이어 캐시 재사용 가능
COPY pyproject.toml uv.lock ./

# 프로덕션 의존성만 설치 (dev 제외, 프로젝트 자체는 미설치)
RUN uv sync --frozen --no-dev --no-install-project

# 소스 코드 복사
COPY app/ ./app/
COPY static/ ./static/
COPY alembic/ ./alembic/
COPY alembic.ini ./

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
