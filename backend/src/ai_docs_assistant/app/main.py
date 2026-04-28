import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor

from ai_docs_assistant.app.logger import logger
from ai_docs_assistant.app.schemas import SearchRequest, SearchResponse
from ai_docs_assistant.app.rag import initialize_rag_from_docs, search_documentation


@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info('Инициализация RAG из docs/')

    # Выполняем загрузку эмбеддингов в отдельном потоке
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        await loop.run_in_executor(executor=executor, func=initialize_rag_from_docs)

    logger.info('Сервис готов к работе')
    yield


app = FastAPI(
    title='AI Docs Assistant',
    lifespan=lifespan,
)


@app.get('/health')
def health_check():
    return {'status': 'ok'}


@app.post('/search', response_model=SearchResponse)
def search_docs(request: SearchRequest):
    """
    Выполняет семантический поиск в базе документации.
    """
    result = search_documentation(request.query)

    if result:
        return SearchResponse(found=True, content=result)
    else:
        return SearchResponse(
            found=False,
            message='Документация не найдена. Используйте /generate для создания новой.'
        )

