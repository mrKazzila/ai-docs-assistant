FROM python:3.13-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

RUN pip install --upgrade pip setuptools wheel

COPY pyproject.toml ./
COPY src ./src

RUN pip wheel . --wheel-dir /wheels


FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN groupadd --system app \
    && useradd --system --gid app --create-home --home-dir /app app

WORKDIR /app

COPY --from=builder /wheels /wheels

RUN pip install --no-cache-dir /wheels/*.whl \
    && rm -rf /wheels \
    && mkdir -p /app/docs /app/logs

RUN chown -R app:app /app

USER app

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "ai_docs_assistant.entrypoints.application.__main__:app", "--host", "0.0.0.0", "--port", "8000"]
