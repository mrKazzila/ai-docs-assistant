# ai-docs-assistant

[Read this README in Russian](README.ru.md)

Local FastAPI service for generating, storing, and semantically searching API documentation. The current implementation lives in `backend/` and uses a layered architecture with separate API, indexer, and background generation worker entrypoints.

## What the service does

- Accepts documentation generation requests via `POST /generate`
- Stores generation jobs in Redis and returns a job id immediately
- Processes queued generation jobs in a separate background worker
- Exposes generation job status and result via `GET /generate/{job_id}`
- Stores Markdown documents in `backend/docs/`
- Indexes documents in Qdrant for semantic search
- Finds the most relevant documentation via `POST /search` using multi-candidate selection and relevance filtering
- Checks service dependencies and RAG readiness via `GET /health`

## Architecture

The backend is split into explicit layers:

- `presentation` exposes the FastAPI REST API and request/response schemas
- `application` contains DTOs, ports, use cases, and application services
- `domain` contains document policies, job entities, and enums
- `infrastructure` implements storage, vector search, Redis-backed queues and repositories, health probing, and CrewAI-based generation
- `entrypoints` contains runtime entrypoints for the API and workers
- `config` contains settings, modular dependency factories, and logging setup

The service uses these runtime components:

- `FastAPI` for the HTTP API
- `Redis` for generation-job queueing and job state storage
- `generation-worker` for background processing of queued generation jobs
- `CrewAI` to run generator and validator agents inside `CrewAIDocumentGenerator`
- `Ollama` for the LLM and embedding model
- `Qdrant` for vector storage and semantic search
- local filesystem storage in `backend/docs/` for the Markdown knowledge base
- `SearchResultSelector` to choose the best candidate from multiple search hits
- `SearchRelevancePolicy` to reject semantically inconsistent search results

Important runtime behavior:

- The API entrypoint is `python -m ai_docs_assistant.entrypoints.application`
- The knowledge-base indexing worker is `python -m ai_docs_assistant.entrypoints.workers.indexer`
- The background generation worker is `python -m ai_docs_assistant.entrypoints.workers.generation`
- Seed documents are indexed by the separate indexer worker, not implicitly during API startup
- Generation flow is asynchronous: API creates a job, Redis stores the queue entry and job state, the worker processes the job, and the API exposes the result by job id
- Search flow is multi-step: fetch several Qdrant candidates, choose the best match, then validate relevance before returning content

## Stack

- Python 3.13
- FastAPI
- Uvicorn
- Redis
- CrewAI
- Ollama
- Qdrant
- LangChain (`langchain-ollama`, `langchain-qdrant`)
- Structlog
- `uv`
- `just`
- Docker Compose

## Project structure

```text
.
├── README.md
├── README.ru.md
└── backend/
    ├── docker-compose.yml
    ├── Dockerfile
    ├── docs/
    ├── env/
    ├── just/
    ├── logs/
    ├── lora-adapter/
    ├── pyproject.toml
    ├── qdrant_storage/
    ├── redis_data/
    ├── src/
    └── uv.lock
```

Key directories:

- `backend/src/ai_docs_assistant/presentation/` - REST API layer
- `backend/src/ai_docs_assistant/application/` - use cases, DTOs, interfaces, and search-related application services
- `backend/src/ai_docs_assistant/domain/` - domain policies, entities, and enums
- `backend/src/ai_docs_assistant/infrastructure/` - Qdrant, filesystem storage, Redis queue/repository, CrewAI generator, and health checks
- `backend/src/ai_docs_assistant/entrypoints/` - API, indexer, and generation-worker entrypoints
- `backend/src/ai_docs_assistant/config/` - settings, modular dependency factories (`config.dependencies.api/common/generation/indexer/facade`), and logging
- `backend/docs/` - seed and generated Markdown documents
- `backend/env/.env` - environment configuration loaded by the application and Docker services
- `backend/just/` - grouped `just` command definitions
- `backend/logs/` - application log files
- `backend/lora-adapter/` - optional Ollama LoRA adapter assets and setup notes
- `backend/qdrant_storage/` - local Qdrant data directory mounted by Docker Compose
- `backend/redis_data/` - local Redis persistence directory mounted by Docker Compose

## Quick start

### Requirements

- Python `>=3.13,<3.14`
- `uv`
- `just`
- Docker Compose
- installed and running `Ollama` on the host machine

### Recommended Docker-first workflow

1. Move into the backend directory:

```bash
cd backend
```

2. Install Python dependencies:

```bash
uv sync
```

3. Pull the embedding model:

```bash
ollama pull mxbai-embed-large
```

4. Prepare the generation model.

By default, `backend/env/.env` expects:

```env
OLLAMA_MODEL=ollama/my_api_docs
```

If that model does not exist locally, use the optional instructions in [`backend/lora-adapter/README.md`](/Users/ikaz/work/courses/ai-docs-assistant/backend/lora-adapter/README.md).

5. Start the full stack:

```bash
just run-all
```

This flow starts:

- `qdrant`
- `redis`
- the separate one-off `indexer` job that loads `backend/docs/` into Qdrant
- the long-lived `generation-worker` container for background job processing
- the `api` container on `http://127.0.0.1:8000`

If `generation-worker` is not running, generation jobs remain in `pending` and no document will be produced.

The `indexer` runs like a migration: it starts, finishes indexing, and is removed automatically, so `just ps` shows only the long-lived `qdrant`, `redis`, `generation-worker`, and `api` services afterward.
If you previously started `indexer` with `docker compose up`, run `just down-all` once to clear the old service container before relying on the one-off workflow.

Useful stack commands:

- `just run-qdrant`
- `just run-redis`
- `just run-indexer`
- `just run-api`
- `just run-all`
- `just down-all`
- `just ps`
- `just stack-restart`
- `just rebuild-indexer-api`
- `just rebuild-all`

Useful quality commands:

- `just lint`
- `just format-check`
- `just typecheck`
- `just quality`

### Equivalent manual Docker Compose flow

From `backend/`:

1. Start Qdrant:

```bash
docker compose up -d qdrant
```

2. Start Redis:

```bash
docker compose up -d redis
```

3. Run the indexer:

```bash
docker compose build indexer
docker compose run --rm --no-deps indexer
```

4. Start the generation worker:

```bash
docker compose build generation-worker
docker compose up -d generation-worker
```

5. Start the API:

```bash
docker compose build api
docker compose up -d api
```

The API, Redis, and generation worker are all required for asynchronous generation. In the Docker-based setup, the default `backend/env/.env` uses:

```env
OLLAMA_HOST=host.docker.internal
REDIS_HOST=redis
```

This manual flow matches the current `just` recipes: `qdrant` and `redis` stay running in detached mode, `indexer` runs as a one-off container, and `generation-worker` plus `api` start separately afterward.

## Configuration

Application settings are loaded from [`backend/env/.env`](/Users/ikaz/work/courses/ai-docs-assistant/backend/env/.env).

| Variable | Purpose |
| --- | --- |
| `QDRANT_HOST` | Qdrant host |
| `QDRANT_PORT` | Qdrant port |
| `QDRANT_COLLECTION_NAME` | Qdrant collection name |
| `EMBEDDING_MODEL_NAME` | Ollama embedding model used for indexing and search |
| `VECTOR_SIZE` | vector size for the Qdrant collection |
| `API_KEY` | API key passed into the Ollama-backed CrewAI LLM client |
| `OLLAMA_HOST` | Ollama host |
| `OLLAMA_PORT` | Ollama port |
| `OLLAMA_MODEL` | model name used for documentation generation |
| `REDIS_HOST` | Redis host |
| `REDIS_PORT` | Redis port |
| `REDIS_DB` | Redis database index for generation jobs |
| `REDIS_GENERATION_QUEUE_NAME` | Redis list name used as the generation queue |
| `REDIS_GENERATION_JOB_TTL_SECONDS` | TTL for stored generation job state in Redis |

Derived URLs are assembled in settings:

- `qdrant_url = http://{QDRANT_HOST}:{QDRANT_PORT}`
- `ollama_url = http://{OLLAMA_HOST}:{OLLAMA_PORT}`

## Runtime entrypoints

- API: `python -m ai_docs_assistant.entrypoints.application`
- Indexer: `python -m ai_docs_assistant.entrypoints.workers.indexer`
- Generation worker: `python -m ai_docs_assistant.entrypoints.workers.generation`

The indexer also supports:

```bash
python -m ai_docs_assistant.entrypoints.workers.indexer --no-recreate
```

That mode keeps the existing Qdrant collection instead of recreating it before indexing.

## API

### `POST /generate`

Creates a new asynchronous generation job.

Request example:

```json
{
  "query": "describe the endpoint for getting user tasks"
}
```

Successful response:

```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "pending"
}
```

Behavior:

- creates a generation job with status `pending`
- stores the job state in Redis
- enqueues the job id into the Redis generation queue
- returns `202 Accepted` immediately
- does not generate the document inline in the API request

### `GET /generate/{job_id}`

Returns the current job state and, when available, the generation result.

Response example for a completed job:

```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "query": "describe the endpoint for getting user tasks",
  "status": "completed",
  "content": "### GET /api/v1/tasks\n**Описание**: ...",
  "file_path": "docs/get_tasks_1.md",
  "error_message": null
}
```

Possible statuses:

- `pending`
- `processing`
- `completed`
- `failed`
- `skipped`

Status meaning:

- `completed` - the document was generated, saved, and indexed
- `failed` - generation or validation failed
- `skipped` - a sufficiently similar document already existed, so no new file was created

Returns `404 Not Found` when the job does not exist.

### `POST /search`

Searches for the most relevant indexed document through a multi-candidate selection flow.

Request example:

```json
{
  "query": "endpoint for getting profile"
}
```

Response when a document is found:

```json
{
  "found": true,
  "content": "### GET /api/v1/profile\n**Описание**: Возвращает профиль авторизованного пользователя.\n...",
  "message": null
}
```

Response when nothing is found:

```json
{
  "found": false,
  "content": null,
  "message": "Документация не найдена. Используйте /generate для создания новой."
}
```

Behavior:

- requests up to 5 candidates from the vector index through `search_many(...)` with `score_threshold=0.0`
- uses `SearchResultSelector` to choose the best candidate for the query
- if the query clearly refers to `profile`, `task`, or `user`, the selector prefers a result whose `content` or `source` contains the matching path/token
- if there is no explicit preferred match, the selector falls back to the first candidate returned by the index
- uses `SearchRelevancePolicy` to validate the selected result before returning it
- rejects results with score lower than `0.62`
- additionally checks that the detected domain (`profile`, `users`, `tasks`) and action (`get`, `create`, `update`, `delete`) from the query match the selected document
- returns `found: false` when there are no candidates or when the chosen candidate fails relevance validation

Operational notes:

- `search_many()` has replaced the old single-result strategy for user-facing search
- the simpler `search()` method is still used in other parts of the system, including generation deduplication and health checks
- for `/search`, “not found” can now mean either an empty candidate set or a candidate rejected by selector/policy validation

### `GET /health`

Checks dependency availability and basic RAG readiness.

Response example:

```json
{
  "status": "healthy",
  "checks": {
    "qdrant": true,
    "ollama": true,
    "docs": true,
    "rag_canary": true
  }
}
```

What it checks:

- Qdrant REST availability through `/collections`
- Ollama availability through `/api/tags`
- presence of Markdown files in `backend/docs/`
- a RAG canary query using `Эндпоинт для получения профиля`

## Logs and data

- `backend/logs/app.log` - application informational logs
- `backend/logs/errors.log` - application error logs
- `backend/docs/` - seed and generated Markdown documents
- `backend/qdrant_storage/` - local Qdrant storage
- `backend/redis_data/` - local Redis persistence data

## Seed documents

The repository already includes initial Markdown documents in `backend/docs/`, including:

- `get_profile.md`
- `get_tasks.md`
- `create_task.md`
- `update_task.md`
- `get_users.md`
- `delete_user.md`

They serve as the initial knowledge base for the indexer and support the health-check canary.
