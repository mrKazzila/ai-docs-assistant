# ai-docs-assistant

[Read this README in English](README.md)

Локальный FastAPI-сервис для генерации, хранения и семантического поиска API-документации. Текущая реализация находится в `backend/` и организована как layered application с отдельными entrypoint'ами для API и индексатора.

## Что умеет сервис

- Генерировать Markdown-документацию API по текстовому запросу через `POST /generate`
- Искать в векторном индексе уже существующий релевантный документ до генерации нового
- Валидировать сгенерированный контент перед сохранением в локальную базу знаний
- Сохранять Markdown-документы в `backend/docs/`
- Индексировать документы в Qdrant для semantic search
- Находить наиболее релевантную документацию через `POST /search`
- Проверять зависимости и готовность RAG через `GET /health`

## Архитектура

Бэкенд разделён на явные слои:

- `presentation` публикует FastAPI REST API и схемы запросов/ответов
- `application` содержит DTO, порты и use case'ы
- `domain` содержит политики документов и правила именования файлов
- `infrastructure` реализует storage, vector search, health probing и генерацию на базе CrewAI
- `entrypoints` содержит runtime entrypoint'ы для API и worker-индексатора
- `config` содержит settings, wiring зависимостей и настройку логирования

Сервис использует следующие runtime-компоненты:

- `FastAPI` для HTTP API
- `CrewAI` для запуска generator и validator agents внутри `CrewAIDocumentGenerator`
- `Ollama` для LLM и embedding-модели
- `Qdrant` для векторного хранилища и semantic search
- локальное файловое хранилище в `backend/docs/` для Markdown-базы знаний

Важно для runtime-поведения:

- entrypoint API: `python -m ai_docs_assistant.entrypoints.application`
- worker индексирования базы знаний: `python -m ai_docs_assistant.entrypoints.workers.indexer`
- seed-документы индексируются отдельным worker'ом, а не неявно при старте API

## Стек

- Python 3.13
- FastAPI
- Uvicorn
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
    ├── src/
    └── uv.lock
```

Ключевые директории:

- `backend/src/ai_docs_assistant/presentation/` - REST API слой
- `backend/src/ai_docs_assistant/application/` - use case'ы, DTO и интерфейсы
- `backend/src/ai_docs_assistant/domain/` - доменные политики и value objects
- `backend/src/ai_docs_assistant/infrastructure/` - Qdrant, файловое хранилище, CrewAI generator и health checks
- `backend/src/ai_docs_assistant/entrypoints/` - entrypoint'ы API и индексатора
- `backend/src/ai_docs_assistant/config/` - settings, фабрики зависимостей и логирование
- `backend/docs/` - seed- и сгенерированные Markdown-документы
- `backend/env/.env` - конфигурация окружения, которую читает приложение и Docker-сервисы
- `backend/just/` - группированные определения команд `just`
- `backend/logs/` - файлы логов приложения
- `backend/lora-adapter/` - опциональные артефакты LoRA-адаптера для Ollama и инструкция по настройке
- `backend/qdrant_storage/` - локальный каталог данных Qdrant, примонтированный через Docker Compose

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
- одноразовый `indexer`-job, который загружает `backend/docs/` в Qdrant
- контейнер `api` на `http://127.0.0.1:8000`

`indexer` работает по принципу миграции: стартует, завершает индексацию и автоматически удаляется, поэтому после выполнения `just ps` показывает только долгоживущие сервисы `qdrant` и `api`.
Если раньше `indexer` запускался через `docker compose up`, один раз выполните `just down-all`, чтобы убрать старый service-контейнер и перейти на одноразовый сценарий.

Полезные команды стека:

- `just run-qdrant`
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

2. Запустите индексатор:

```bash
docker compose build indexer
docker compose run --rm --no-deps indexer
```

3. Запустите API:

```bash
docker compose build api
docker compose up -d api
```

API и indexer работают как отдельные контейнеры. Оба ожидают, что Ollama доступен на хост-машине. В Docker-сценарии дефолтный `backend/env/.env` использует:

```env
OLLAMA_HOST=host.docker.internal
```

Этот ручной сценарий соответствует текущим `just`-рецептам: сначала собираются образы, затем в фоне поднимается `qdrant`, после этого одноразово выполняется `indexer`, и отдельно запускается `api`.

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

Производные URL собираются в settings:

- `qdrant_url = http://{QDRANT_HOST}:{QDRANT_PORT}`
- `ollama_url = http://{OLLAMA_HOST}:{OLLAMA_PORT}`

## Runtime entrypoints

- API: `python -m ai_docs_assistant.entrypoints.application`
- Indexer: `python -m ai_docs_assistant.entrypoints.workers.indexer`

Индексатор также поддерживает:

```bash
python -m ai_docs_assistant.entrypoints.workers.indexer --no-recreate
```

В этом режиме существующая коллекция Qdrant не пересоздаётся перед индексацией.

## API

### `POST /generate`

Генерирует новый Markdown-документ, если достаточно похожий документ ещё не найден.

Пример запроса:

```json
{
  "query": "опиши endpoint для получения задач пользователя"
}
```

Успешный ответ:

```json
{
  "success": true,
  "message": "Документ успешно создан и сохранён.",
  "content": "### GET /api/v1/tasks\n**Описание**: ...",
  "file_path": "docs/get_tasks_1.md"
}
```

Поведение:

- сначала выполняет semantic search через `DocumentIndex`
- использует `CrewAIDocumentGenerator` для генерации контента
- валидирует сгенерированный контент доменным правилом, эквивалентным `content.startswith("###")`
- сохраняет документ с уникальным именем в `backend/docs/`
- индексирует сохранённый документ в Qdrant
- если похожий документ уже найден, возвращает существующий контент и не создаёт новый файл

### `POST /search`

Ищет один наиболее релевантный документ в индексе.

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

## Seed-документы

В репозитории уже есть стартовые Markdown-документы в `backend/docs/`, включая:

- `get_profile.md`
- `get_tasks.md`
- `create_task.md`
- `update_task.md`
- `get_users.md`
- `delete_user.md`

Они служат начальной базой знаний для индексатора и используются health-check canary.
