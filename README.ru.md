# ai-docs-assistant

[Read this README in English](README.md)

Локальный FastAPI-сервис для генерации, хранения и семантического поиска API-документации. Проект использует Ollama для локальной LLM и эмбеддингов, Qdrant как векторное хранилище, а также agent-based workflow на CrewAI для генерации и валидации Markdown-документов.

Основная реализация находится в директории `backend/`.

## Что умеет сервис

- Генерировать Markdown-документацию по текстовому запросу через `POST /generate`
- Проверять результат вторым агентным шагом перед сохранением
- Сохранять новые документы в локальную базу знаний `backend/docs/`
- Индексировать документы в Qdrant для последующего semantic search
- Искать релевантную документацию через `POST /search`
- Проверять доступность зависимостей и базовую работоспособность через `GET /health`

## Архитектура

Сервис состоит из нескольких локальных компонентов:

- `FastAPI` предоставляет HTTP API.
- `Ollama` используется для embedding-модели и для LLM, которая запускает генерацию и валидацию.
- `CrewAI` оркестрирует два агентных шага: `generator` и `validator`.
- `Qdrant` хранит векторный индекс документов.
- `backend/docs/` содержит seed-документацию и новые `.md`-файлы, созданные через API.

При старте приложения вызывается инициализация RAG: сервис читает Markdown-файлы из `docs/` и загружает их в Qdrant.

Фактический entrypoint приложения: `ai_docs_assistant.app.main:app`.

## Стек

- Python 3.13
- FastAPI
- Uvicorn
- Ollama
- Qdrant
- LangChain (`langchain-ollama`, `langchain-qdrant`)
- CrewAI
- `uv`

## Структура проекта

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

Ключевые директории:

- `backend/src/ai_docs_assistant/app/` — код FastAPI-приложения, RAG, агентов, health-check и конфигурации
- `backend/docs/` — локальная база знаний в Markdown
- `backend/lora-adapter/` — файлы и инструкция для локальной модели Ollama с LoRA-адаптером
- `backend/logs/` — текстовые логи приложения
- `backend/qdrant_storage/` — локальные данные Qdrant из Docker Compose

## Быстрый старт

### Требования

- Python `>=3.13,<3.14`
- `uv`
- установленный и запущенный `Ollama`
- `Docker Compose`

### 1. Перейти в backend

```bash
cd backend
```

### 2. Установить зависимости

```bash
uv sync
```

### 3. Поднять Qdrant

```bash
docker compose up -d
```

Команда использует [`backend/docker-compose.yml`](/Users/ikaz/work/courses/ai-docs-assistant/backend/docker-compose.yml).

### 4. Загрузить embedding-модель для поиска

```bash
ollama pull mxbai-embed-large
```

### 5. Подготовить LLM для генерации

По умолчанию сервис ожидает модель `ollama/my_api_docs`, указанную в `backend/.env`.

Если такой модели нет, используйте инструкцию из [`backend/lora-adapter/README.md`](/Users/ikaz/work/courses/ai-docs-assistant/backend/lora-adapter/README.md). В текущем репозитории там описан вариант на базе `mistral:7b-instruct-v0.3-q4_K_M` и локального LoRA-адаптера.

### 6. Запустить backend

Запускать сервис нужно из директории `backend/`, так как `.env`, `docs/` и `logs/` читаются через относительные пути.

```bash
uv run uvicorn ai_docs_assistant.app.main:app --reload
```

После запуска сервис будет доступен по адресу `http://127.0.0.1:8000`.

## Конфигурация

Сервис читает настройки из [`backend/.env`](/Users/ikaz/work/courses/ai-docs-assistant/backend/.env).

| Переменная | Назначение |
| --- | --- |
| `QDRANT_HOST` | хост Qdrant |
| `QDRANT_PORT` | порт Qdrant |
| `QDRANT_COLLECTION_NAME` | имя коллекции векторного индекса |
| `EMBEDDING_MODEL_NAME` | имя embedding-модели Ollama |
| `VECTOR_SIZE` | размер вектора для коллекции Qdrant |
| `API_KEY` | API key, который передаётся в LLM-клиент CrewAI/Ollama |
| `OLLAMA_HOST` | хост Ollama |
| `OLLAMA_PORT` | порт Ollama |
| `OLLAMA_MODEL` | имя модели для генерации документации |

Производные URL формируются внутри приложения:

- `qdrant_url = http://{QDRANT_HOST}:{QDRANT_PORT}`
- `ollama_url = http://{OLLAMA_HOST}:{OLLAMA_PORT}`

## API

### `POST /generate`

Генерирует новый документ, валидирует его и при успехе сохраняет в `docs/` с последующей индексацией в Qdrant.

Пример запроса:

```json
{
  "query": "опиши эндпоинт для получения задач пользователя"
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

Ответ при ошибке:

```json
{
  "success": false,
  "message": "Ошибка генерации: ..."
}
```

Поведение:

- перед генерацией сервис делает поиск похожего документа;
- если документ уже найден с порогом похожести `0.75`, новый файл не создаётся;
- сгенерированный документ должен начинаться с `###`, иначе он считается невалидным;
- имя файла строится из запроса через внутренний slugify-механизм.

### `POST /search`

Ищет наиболее релевантный документ в Qdrant через semantic search.

Пример запроса:

```json
{
  "query": "эндпоинт для получения профиля"
}
```

Ответ, если документ найден:

```json
{
  "found": true,
  "content": "### GET /api/v1/profile\n**Описание**: Возвращает профиль авторизованного пользователя.\n..."
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

Проверяет состояние сервиса и зависимостей.

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

- доступность REST API Qdrant;
- доступность Ollama;
- наличие Markdown-файлов в `docs/`;
- canary-запрос к RAG с ожиданием, что в базе находится документация для `GET /api/v1/profile`.

## Логи и данные

- `backend/logs/app.log` — информационные сообщения приложения
- `backend/logs/errors.log` — ошибки приложения
- `backend/docs/` — исходные и сгенерированные Markdown-документы
- `backend/qdrant_storage/` — локальное хранилище данных Qdrant

## Работа с seed-документами

В репозитории уже есть примеры документов в `backend/docs/`, например:

- `get_profile.md`
- `get_tasks.md`
- `create_task.md`
- `update_task.md`
- `get_users.md`
- `delete_user.md`

Они используются как начальная база знаний для semantic search и для canary-проверки в `/health`.

## Roadmap / Возможные улучшения

- Сделать `POST /generate` асинхронным через фоновые задачи и polling-статус
- Добавить reranking поверх базового similarity search
- Реализовать полноценный Docker-образ для backend
- Добавить реальные тесты `pytest` для API, RAG и workflow генерации
- Перевести логи на JSON-формат и добавить метрики/наблюдаемость
- Добавить UI для поиска, генерации и редактирования документов

## Примечания по реализации

- Векторная коллекция создаётся с `Distance.COSINE`.
- Для поиска используется `similarity_search_with_score`.
- Новые документы после сохранения индексируются сразу через `add_document_to_index(...)`.
- Имена файлов строятся эвристически по ключевым словам запроса, например `get_user`, `create_task`, `delete_user`.
