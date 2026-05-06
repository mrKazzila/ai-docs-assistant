# ai-docs-assistant

[Read this README in English](README.md)

Локальный FastAPI-сервис для генерации, хранения и семантического поиска API-документации. Текущая реализация находится в `backend/` и использует layered architecture с отдельными entrypoint'ами для API, индексатора и фонового generation worker.

## Что умеет сервис

- Принимать запросы на генерацию документации через `POST /generate`
- Сохранять generation jobs в Redis и сразу возвращать job id
- Обрабатывать queued jobs в отдельном фоновом worker'е
- Отдавать статус и результат generation job через `GET /generate/{job_id}`
- Сохранять Markdown-документы в `backend/docs/`
- Индексировать документы в Qdrant для semantic search
- Находить наиболее релевантную документацию через `POST /search` с multi-candidate выбором и relevance filtering
- Проверять зависимости и готовность RAG через `GET /health`

## Архитектура

Бэкенд разделён на явные слои:

- `presentation` публикует FastAPI REST API и схемы запросов/ответов
- `application` содержит DTO, порты, use case'ы и application services
- `domain` содержит политики документов, job entities и enum'ы
- `infrastructure` реализует storage, vector search, Redis-backed queue/repository, health probing и генерацию на базе CrewAI
- `entrypoints` содержит runtime entrypoint'ы для API и worker'ов
- `config` содержит settings, модульные фабрики зависимостей и настройку логирования

Сервис использует следующие runtime-компоненты:

- `FastAPI` для HTTP API
- `Redis` для очереди generation jobs и хранения их состояния
- `generation-worker` для фоновой обработки queued generation jobs
- `CrewAI` для запуска generator и validator agents внутри `CrewAIDocumentGenerator`
- `Ollama` для LLM и embedding-модели
- `Qdrant` для векторного хранилища и semantic search
- локальное файловое хранилище в `backend/docs/` для Markdown-базы знаний
- `SearchResultSelector` для выбора лучшего кандидата из нескольких search results
- `SearchRelevancePolicy` для отбраковки семантически нерелевантных результатов

Важно для runtime-поведения:

- entrypoint API: `python -m ai_docs_assistant.entrypoints.application`
- worker индексирования базы знаний: `python -m ai_docs_assistant.entrypoints.workers.indexer`
- фоновый generation worker: `python -m ai_docs_assistant.entrypoints.workers.generation`
- seed-документы индексируются отдельным worker'ом, а не неявно при старте API
- flow генерации асинхронный: API создаёт job, Redis хранит очередь и состояние job, worker выполняет обработку, а API отдаёт результат по job id
- flow поиска многошаговый: сначала запрашиваются несколько кандидатов из Qdrant, затем выбирается лучший match, после чего результат проходит проверку релевантности

## Стек

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

## Структура проекта

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

Ключевые директории:

- `backend/src/ai_docs_assistant/presentation/` - REST API слой
- `backend/src/ai_docs_assistant/application/` - use case'ы, DTO, интерфейсы и application services для поиска
- `backend/src/ai_docs_assistant/domain/` - доменные политики, сущности и enum'ы
- `backend/src/ai_docs_assistant/infrastructure/` - Qdrant, файловое хранилище, Redis queue/repository, CrewAI generator и health checks
- `backend/src/ai_docs_assistant/entrypoints/` - entrypoint'ы API, индексатора и generation worker
- `backend/src/ai_docs_assistant/config/` - settings, модульные фабрики зависимостей (`config.dependencies.api/common/generation/indexer/facade`) и логирование
- `backend/docs/` - seed- и сгенерированные Markdown-документы
- `backend/env/.env` - конфигурация окружения, которую читает приложение и Docker-сервисы
- `backend/just/` - группированные определения команд `just`
- `backend/logs/` - файлы логов приложения
- `backend/lora-adapter/` - опциональные артефакты LoRA-адаптера для Ollama и инструкция по настройке
- `backend/qdrant_storage/` - локальный каталог данных Qdrant, примонтированный через Docker Compose
- `backend/redis_data/` - локальный каталог Redis persistence, примонтированный через Docker Compose

## Быстрый старт

### Требования

- Python `>=3.13,<3.14`
- `uv`
- `just`
- Docker Compose
- установленный и запущенный `Ollama` на хост-машине

### Рекомендуемый Docker-first сценарий

1. Перейдите в директорию backend:

```bash
cd backend
```

2. Установите Python-зависимости:

```bash
uv sync
```

3. Скачайте embedding-модель:

```bash
ollama pull mxbai-embed-large
```

4. Подготовьте модель для генерации.

По умолчанию `backend/env/.env` ожидает:

```env
OLLAMA_MODEL=ollama/my_api_docs
```

Если такой модели локально нет, используйте опциональную инструкцию из [`backend/lora-adapter/README.md`](/Users/ikaz/work/courses/ai-docs-assistant/backend/lora-adapter/README.md).

5. Поднимите весь стек:

```bash
just run-all
```

Этот сценарий запускает:

- `qdrant`
- `redis`
- отдельный одноразовый `indexer`-job, который загружает `backend/docs/` в Qdrant
- долгоживущий контейнер `generation-worker` для фоновой обработки jobs
- контейнер `api` на `http://127.0.0.1:8000`

Если `generation-worker` не запущен, generation jobs останутся в `pending`, и документ не будет создан.

`indexer` работает по принципу миграции: стартует, завершает индексацию и автоматически удаляется, поэтому после выполнения `just ps` показывает только долгоживущие сервисы `qdrant`, `redis`, `generation-worker` и `api`.
Если раньше `indexer` запускался через `docker compose up`, один раз выполните `just down-all`, чтобы убрать старый service-контейнер и перейти на одноразовый сценарий.

Полезные команды стека:

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

Полезные команды quality-проверок:

- `just lint`
- `just format-check`
- `just typecheck`
- `just quality`

### Эквивалентный ручной сценарий через Docker Compose

Из `backend/`:

1. Запустите Qdrant:

```bash
docker compose up -d qdrant
```

2. Запустите Redis:

```bash
docker compose up -d redis
```

3. Запустите индексатор:

```bash
docker compose build indexer
docker compose run --rm --no-deps indexer
```

4. Запустите generation worker:

```bash
docker compose build generation-worker
docker compose up -d generation-worker
```

5. Запустите API:

```bash
docker compose build api
docker compose up -d api
```

Для асинхронной генерации нужны одновременно API, Redis и generation worker. В Docker-сценарии дефолтный `backend/env/.env` использует:

```env
OLLAMA_HOST=host.docker.internal
REDIS_HOST=redis
```

Этот ручной сценарий соответствует текущим `just`-рецептам: `qdrant` и `redis` работают в фоне, `indexer` выполняется как одноразовый контейнер, а `generation-worker` и `api` запускаются отдельно после него.

## Конфигурация

Настройки приложения загружаются из [`backend/env/.env`](/Users/ikaz/work/courses/ai-docs-assistant/backend/env/.env).

| Variable | Назначение |
| --- | --- |
| `QDRANT_HOST` | хост Qdrant |
| `QDRANT_PORT` | порт Qdrant |
| `QDRANT_COLLECTION_NAME` | имя коллекции Qdrant |
| `EMBEDDING_MODEL_NAME` | Ollama embedding-модель для индексации и поиска |
| `VECTOR_SIZE` | размер вектора для коллекции Qdrant |
| `API_KEY` | API key, который передаётся в Ollama-backed CrewAI LLM client |
| `OLLAMA_HOST` | хост Ollama |
| `OLLAMA_PORT` | порт Ollama |
| `OLLAMA_MODEL` | имя модели для генерации документации |
| `REDIS_HOST` | хост Redis |
| `REDIS_PORT` | порт Redis |
| `REDIS_DB` | индекс Redis database для generation jobs |
| `REDIS_GENERATION_QUEUE_NAME` | имя Redis list, используемой как очередь генерации |
| `REDIS_GENERATION_JOB_TTL_SECONDS` | TTL для хранения состояния generation jobs в Redis |

Производные URL собираются в settings:

- `qdrant_url = http://{QDRANT_HOST}:{QDRANT_PORT}`
- `ollama_url = http://{OLLAMA_HOST}:{OLLAMA_PORT}`

## Runtime entrypoints

- API: `python -m ai_docs_assistant.entrypoints.application`
- Indexer: `python -m ai_docs_assistant.entrypoints.workers.indexer`
- Generation worker: `python -m ai_docs_assistant.entrypoints.workers.generation`

Индексатор также поддерживает:

```bash
python -m ai_docs_assistant.entrypoints.workers.indexer --no-recreate
```

В этом режиме существующая коллекция Qdrant не пересоздаётся перед индексацией.

## API

### `POST /generate`

Создаёт новую асинхронную generation job.

Пример запроса:

```json
{
  "query": "опиши endpoint для получения задач пользователя"
}
```

Успешный ответ:

```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "pending"
}
```

Поведение:

- создаёт generation job со статусом `pending`
- сохраняет состояние job в Redis
- ставит `job_id` в Redis generation queue
- сразу возвращает `202 Accepted`
- не выполняет генерацию документа inline внутри API-запроса

### `GET /generate/{job_id}`

Возвращает текущее состояние job и, когда он готов, результат генерации.

Пример ответа для завершённой job:

```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "query": "опиши endpoint для получения задач пользователя",
  "status": "completed",
  "content": "### GET /api/v1/tasks\n**Описание**: ...",
  "file_path": "docs/get_tasks_1.md",
  "error_message": null
}
```

Возможные статусы:

- `pending`
- `processing`
- `completed`
- `failed`
- `skipped`

Значение статусов:

- `completed` - документ был сгенерирован, сохранён и проиндексирован
- `failed` - генерация или валидация завершилась ошибкой
- `skipped` - похожий документ уже существовал, поэтому новый файл не создавался

Если job не существует, endpoint возвращает `404 Not Found`.

### `POST /search`

Ищет наиболее релевантный документ через многошаговый multi-candidate flow.

Пример запроса:

```json
{
  "query": "endpoint для получения профиля"
}
```

Ответ, если документ найден:

```json
{
  "found": true,
  "content": "### GET /api/v1/profile\n**Описание**: Возвращает профиль авторизованного пользователя.\n...",
  "message": null
}
```

Ответ, если ничего не найдено:

```json
{
  "found": false,
  "content": null,
  "message": "Документация не найдена. Используйте /generate для создания новой."
}
```

Поведение:

- запрашивает у векторного индекса до 5 кандидатов через `search_many(...)` с `score_threshold=0.0`
- использует `SearchResultSelector`, чтобы выбрать лучший кандидат для текущего запроса
- если в запросе явно распознаётся `profile`, `task` или `user`, selector предпочитает документ, в котором соответствующий path/token есть в `content` или `source`
- если явного предпочтительного совпадения нет, selector берёт первый кандидат из выдачи индекса
- использует `SearchRelevancePolicy`, чтобы провалидировать выбранный результат перед возвратом
- отбрасывает результаты со score ниже `0.62`
- дополнительно проверяет, что домен (`profile`, `users`, `tasks`) и действие (`get`, `create`, `update`, `delete`), распознанные в запросе, согласуются с выбранным документом
- возвращает `found: false`, если кандидатов нет или если выбранный кандидат не прошёл relevance validation

Operational notes:

- `search_many()` логически заменил старую стратегию поиска с одним прямым результатом для пользовательского `/search`
- более простой `search()` по-прежнему используется в других частях системы, включая проверку дубликатов при генерации и health check
- для `/search` отсутствие результата теперь может означать либо пустую выдачу, либо кандидата, отфильтрованного selector/policy-проверкой

### `GET /health`

Проверяет доступность зависимостей и базовую готовность RAG.

Пример ответа:

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

Что проверяется:

- доступность Qdrant через `/collections`
- доступность Ollama через `/api/tags`
- наличие Markdown-файлов в `backend/docs/`
- canary-запрос к RAG с текстом `Эндпоинт для получения профиля`

## Логи и данные

- `backend/logs/app.log` - информационные логи приложения
- `backend/logs/errors.log` - логи ошибок приложения
- `backend/docs/` - seed- и сгенерированные Markdown-документы
- `backend/qdrant_storage/` - локальное хранилище данных Qdrant
- `backend/redis_data/` - локальные persistence-данные Redis

## Seed-документы

В репозитории уже есть стартовые Markdown-документы в `backend/docs/`, включая:

- `get_profile.md`
- `get_tasks.md`
- `create_task.md`
- `update_task.md`
- `get_users.md`
- `delete_user.md`

Они служат начальной базой знаний для индексатора и используются health-check canary.
