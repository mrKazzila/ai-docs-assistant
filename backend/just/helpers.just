[group("Internal")]
[private]
[doc("Verify uv is installed")]
_uv-ready:
    @if command -v uv >/dev/null 2>&1; then \
        echo "[uv] CLI found"; \
    else \
        echo "[uv] CLI is missing"; \
        echo "[uv] Install uv and rerun the command"; \
        exit 1; \
    fi

[group("Internal")]
[private]
[doc("Verify Docker daemon is reachable")]
_docker-ready:
    @if docker info >/dev/null 2>&1; then \
        echo "[docker] Docker daemon is reachable"; \
    else \
        echo "[docker] Docker daemon is unavailable"; \
        echo "[docker] Start Docker Desktop or OrbStack and rerun the command"; \
        exit 1; \
    fi

[group("Internal")]
[private]
[doc("Verify Ollama CLI is installed")]
_ollama-ready:
    @if command -v ollama >/dev/null 2>&1; then \
        echo "[ollama] CLI found"; \
    else \
        echo "[ollama] CLI is missing"; \
        echo "[ollama] Install Ollama and rerun the command"; \
        exit 1; \
    fi

[group("Internal")]
[private]
[doc("Verify env/.env exists")]
_env-file-check:
    @if [ -f env/.env ]; then \
        echo "[env] env/.env found"; \
    else \
        echo "[env] Missing env/.env"; \
        echo "[env] Create backend/env/.env and rerun the command"; \
        exit 1; \
    fi

[group("Internal")]
[private]
[doc("Verify docs directory exists")]
_docs-dir-check:
    @if [ -d docs ]; then \
        echo "[docs] docs/ directory found"; \
    else \
        echo "[docs] Missing docs/ directory"; \
        echo "[docs] Create backend/docs/ and rerun the command"; \
        exit 1; \
    fi

[group("Internal")]
[private]
[doc("Create logs directory if needed")]
_logs-dir-create:
    @mkdir -p logs
    @echo "[logs] logs/ directory is ready"

[group("Internal")]
[private]
[doc("Create qdrant storage directory if needed")]
_qdrant-storage-create:
    @mkdir -p qdrant_storage
    @echo "[qdrant] qdrant_storage/ directory is ready"
