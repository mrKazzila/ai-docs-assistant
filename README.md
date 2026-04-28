# ai-docs-assistant

[Read this README in Russian](README.ru.md)

Local FastAPI service for generating, storing, and semantically searching API documentation. The project uses Ollama for a local LLM and embeddings, Qdrant as a vector store, and a CrewAI-based agent workflow to generate and validate Markdown documents.

The main implementation lives in the `backend/` directory.

## What the service does

- Generates Markdown documentation from a text query via `POST /generate`
- Validates the output with a second agent step before saving
- Stores new documents in the local knowledge base at `backend/docs/`
- Indexes documents in Qdrant for semantic search
- Finds relevant documentation via `POST /search`
- Checks dependency availability and basic service health via `GET /health`

## Architecture

The service is composed of several local components:

- `FastAPI` provides the HTTP API.
- `Ollama` is used for the embedding model and for the LLM that performs generation and validation.
- `CrewAI` orchestrates two agent steps: `generator` and `validator`.
- `Qdrant` stores the vector index for the documents.
- `backend/docs/` contains seed documentation and new `.md` files created through the API.

When the application starts, it initializes RAG by reading Markdown files from `docs/` and loading them into Qdrant.

Actual application entrypoint: `ai_docs_assistant.app.main:app`.

## Stack

- Python 3.13
- FastAPI
- Uvicorn
- Ollama
- Qdrant
- LangChain (`langchain-ollama`, `langchain-qdrant`)
- CrewAI
- `uv`

## Project structure

```text
.
├── README.md
├── README.ru.md
└── backend/
    ├── .env
    ├── docker-compose.yml
    ├── docs/
    ├── logs/
    ├── lora-adapter/
    ├── pyproject.toml
    ├── qdrant_storage/
    ├── src/
    └── uv.lock
```

Key directories:

- `backend/src/ai_docs_assistant/app/` — FastAPI app code, RAG, agents, health check, and configuration
- `backend/docs/` — local Markdown knowledge base
- `backend/lora-adapter/` — files and instructions for a local Ollama model with a LoRA adapter
- `backend/logs/` — plain-text application logs
- `backend/qdrant_storage/` — local Qdrant data from Docker Compose

## Quick start

### Requirements

- Python `>=3.13,<3.14`
- `uv`
- installed and running `Ollama`
- `Docker Compose`

### 1. Move into the backend directory

```bash
cd backend
```

### 2. Install dependencies

```bash
uv sync
```

### 3. Start Qdrant

```bash
docker compose up -d
```

This command uses [`backend/docker-compose.yml`](/Users/ikaz/work/courses/ai-docs-assistant/backend/docker-compose.yml).

### 4. Pull the embedding model for search

```bash
ollama pull mxbai-embed-large
```

### 5. Prepare the LLM for generation

By default, the service expects the `ollama/my_api_docs` model specified in `backend/.env`.

If that model is not available, use the instructions in [`backend/lora-adapter/README.md`](/Users/ikaz/work/courses/ai-docs-assistant/backend/lora-adapter/README.md). In the current repository state, that file describes a setup based on `mistral:7b-instruct-v0.3-q4_K_M` and a local LoRA adapter.

### 6. Run the backend

The service should be started from the `backend/` directory because `.env`, `docs/`, and `logs/` are resolved via relative paths.

```bash
uv run uvicorn ai_docs_assistant.app.main:app --reload
```

After startup, the service will be available at `http://127.0.0.1:8000`.

## Configuration

The service reads settings from [`backend/.env`](/Users/ikaz/work/courses/ai-docs-assistant/backend/.env).

| Variable | Purpose |
| --- | --- |
| `QDRANT_HOST` | Qdrant host |
| `QDRANT_PORT` | Qdrant port |
| `QDRANT_COLLECTION_NAME` | vector index collection name |
| `EMBEDDING_MODEL_NAME` | Ollama embedding model name |
| `VECTOR_SIZE` | vector size for the Qdrant collection |
| `API_KEY` | API key passed into the CrewAI/Ollama LLM client |
| `OLLAMA_HOST` | Ollama host |
| `OLLAMA_PORT` | Ollama port |
| `OLLAMA_MODEL` | model name used to generate documentation |

Derived URLs are built inside the application:

- `qdrant_url = http://{QDRANT_HOST}:{QDRANT_PORT}`
- `ollama_url = http://{OLLAMA_HOST}:{OLLAMA_PORT}`

## API

### `POST /generate`

Generates a new document, validates it, and on success saves it to `docs/` and indexes it in Qdrant.

Request example:

```json
{
  "query": "describe the endpoint for getting user tasks"
}
```

Successful response:

```json
{
  "success": true,
  "message": "Документ успешно создан и сохранён.",
  "content": "### GET /api/v1/tasks\n**Описание**: ...",
  "file_path": "docs/get_tasks_1.md"
}
```

Error response:

```json
{
  "success": false,
  "message": "Ошибка генерации: ..."
}
```

Behavior:

- before generation, the service searches for a similar document;
- if a document is already found with a similarity threshold of `0.75`, no new file is created;
- the generated document must start with `###`, otherwise it is considered invalid;
- the filename is derived from the query using an internal slugify mechanism.

### `POST /search`

Finds the most relevant document in Qdrant using semantic search.

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
  "content": "### GET /api/v1/profile\n**Описание**: Возвращает профиль авторизованного пользователя.\n..."
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

### `GET /health`

Checks service and dependency health.

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

- Qdrant REST API availability;
- Ollama availability;
- presence of Markdown files in `docs/`;
- a RAG canary query that expects documentation for `GET /api/v1/profile` to exist in the knowledge base.

## Logs and data

- `backend/logs/app.log` — application informational logs
- `backend/logs/errors.log` — application error logs
- `backend/docs/` — source and generated Markdown documents
- `backend/qdrant_storage/` — local Qdrant data storage

## Working with seed documents

The repository already contains example documents in `backend/docs/`, such as:

- `get_profile.md`
- `get_tasks.md`
- `create_task.md`
- `update_task.md`
- `get_users.md`
- `delete_user.md`

They are used as the initial knowledge base for semantic search and for the canary check in `/health`.

## Roadmap / Possible improvements

- Make `POST /generate` asynchronous with background processing and status polling
- Add reranking on top of the basic similarity search
- Implement a full Docker image for the backend
- Add real `pytest` coverage for the API, RAG, and generation workflow
- Switch logs to JSON and add metrics/observability
- Add a UI for searching, generating, and editing documents

## Implementation notes

- The vector collection is created with `Distance.COSINE`.
- Search uses `similarity_search_with_score`.
- New documents are indexed immediately after saving via `add_document_to_index(...)`.
- Filenames are built heuristically from query keywords, for example `get_user`, `create_task`, `delete_user`.
