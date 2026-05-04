import structlog

from ai_docs_assistant.application.interfaces.document_index import (
    DocumentIndex,
)
from ai_docs_assistant.application.interfaces.document_storage import (
    DocumentStorage,
)
from ai_docs_assistant.application.interfaces.health_checker import (
    HealthChecker,
)
from ai_docs_assistant.infrastructure.health.http_probe import HttpProbe

logger = structlog.get_logger(__name__)


class HttpHealthChecker(HealthChecker):
    def __init__(
        self,
        qdrant_url: str,
        ollama_url: str,
        storage: DocumentStorage,
        document_index: DocumentIndex,
        http_probe: HttpProbe,
    ) -> None:
        self._qdrant_url = qdrant_url
        self._ollama_url = ollama_url
        self._storage = storage
        self._document_index = document_index
        self._http_probe = http_probe

    async def check_qdrant(self) -> bool:
        try:
            return await self._http_probe.is_available(
                f"{self._qdrant_url}/collections",
            )
        except Exception as exc:
            logger.error("qdrant_healthcheck_failed", error=str(exc))
            return False

    async def check_ollama(self) -> bool:
        try:
            return await self._http_probe.is_available(
                f"{self._ollama_url}/api/tags",
            )
        except Exception as exc:
            logger.error("ollama_healthcheck_failed", error=str(exc))
            return False

    async def check_docs(self) -> bool:
        return await self._storage.has_markdown_documents()

    async def check_rag_canary(self) -> bool:
        result = await self._document_index.search(
            query="Эндпоинт для получения профиля",
            score_threshold=0.6,
        )

        logger.warning(
            "rag_canary_unexpected_result",
            expected="GET /api/v1/profile",
            source=result.source,
            score=result.score,
        )

        return result is not None and "GET /api/v1/profile" in result.content
