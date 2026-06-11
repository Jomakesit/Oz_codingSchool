# ── Stage 1: Builder ─────────────────────────────────────────────
# gcc 등 빌드 도구가 필요한 패키지(asyncmy 등) 컴파일
FROM python:3.13-slim AS builder

WORKDIR /code

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# asyncmy(Cython 확장) 컴파일에 필요한 빌드 도구 설치
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

# 의존성 파일 먼저 복사 → 소스 변경 시 이 레이어 캐시 재사용
COPY pyproject.toml uv.lock ./

# 프로덕션 의존성 설치 (.venv 생성)
RUN uv sync --frozen --no-dev --no-install-project


# ── Stage 2: Final ───────────────────────────────────────────────
# gcc 없는 경량 이미지 — Builder의 .venv만 복사
FROM python:3.13-slim

WORKDIR /code

# Builder에서 빌드된 가상환경만 복사 (컴파일된 .so 포함)
COPY --from=builder /code/.venv /code/.venv

# .venv의 실행파일을 PATH에 등록
ENV PATH="/code/.venv/bin:$PATH"

# 소스 코드 복사
COPY app/ ./app/
COPY static/ ./static/
COPY alembic/ ./alembic/
COPY alembic.ini ./

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
