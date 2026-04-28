# ai-docs-assistant
Final AI assignment from the course on LLM, with revisions.


# Скачать модель mxbai-embed-large
```python
ollama pull mxbai-embed-large
```

# Запуск qdrant
```python
docker-compose up -d --build
```

# Запуск backend
```python
uvicorn ai_docs_assistant.app.main:app --reload
```

