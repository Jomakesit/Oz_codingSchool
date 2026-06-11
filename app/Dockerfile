FROM python:3.13-slim AS builder
WORKDIR /code
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
RUN uv pip install torch torchvision Pillow --index-url https://download.pytorch.org/whl/cpu

FROM python:3.13-slim
WORKDIR /code
COPY --from=builder /code/.venv /code/.venv
ENV PATH="/code/.venv/bin:$PATH"
COPY app/ ./app/
COPY static/ ./static/
COPY alembic/ ./alembic/
COPY alembic.ini ./
COPY worker/ ./worker/
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
