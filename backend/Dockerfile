FROM ghcr.io/astral-sh/uv:0.8.15 AS uv


FROM python:3.13-slim AS deps-base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    UV_COMPILE_BYTECODE=0 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv

WORKDIR /build

COPY --from=uv /uv /uvx /bin/
COPY pyproject.toml uv.lock ./


FROM deps-base AS api-deps

RUN uv sync --frozen --no-dev --extra api --no-install-project


FROM deps-base AS indexer-deps

RUN uv sync --frozen --no-dev --extra indexer --no-install-project


FROM deps-base AS generation-deps

RUN uv sync --frozen --no-dev --extra generation --no-install-project


FROM python:3.13-slim AS runtime-base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PATH=/opt/venv/bin:$PATH \
    PYTHONPATH=/app/src

RUN groupadd --system app \
    && useradd --system --gid app --create-home --home-dir /app app

WORKDIR /app

COPY src /app/src

RUN mkdir -p /app/docs /app/logs \
    && chown -R app:app /app

USER app


FROM runtime-base AS api-runtime

COPY --from=api-deps /opt/venv /opt/venv

EXPOSE 8000

CMD ["python", "-m", "ai_docs_assistant.entrypoints.application"]


FROM runtime-base AS indexer-runtime

COPY --from=indexer-deps /opt/venv /opt/venv

CMD ["python", "-m", "ai_docs_assistant.entrypoints.workers.indexer"]


FROM runtime-base AS generation-runtime

COPY --from=generation-deps /opt/venv /opt/venv

CMD ["python", "-m", "ai_docs_assistant.entrypoints.workers.generation"]
