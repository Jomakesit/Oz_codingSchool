FROM python:3.13-slim
WORKDIR /code
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
RUN uv pip install torch torchvision Pillow --index-url https://download.pytorch.org/whl/cpu
RUN uv pip install redis
ENV PATH="/code/.venv/bin:$PATH"
COPY worker/ ./worker/
CMD ["python", "-m", "worker.main"]
