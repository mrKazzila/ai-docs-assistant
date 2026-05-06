import uuid

import structlog
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from ai_docs_assistant.application.interfaces.document_index import (
    DocumentIndex,
    IndexedDocument,
)

logger = structlog.get_logger(__name__)


class QdrantDocumentIndex(DocumentIndex):
    def __init__(
        self,
        host: str,
        port: int,
        collection_name: str,
        embedding_model_name: str,
        vector_size: int,
    ) -> None:
        self._collection_name = collection_name
        self._vector_size = vector_size

        self._client = QdrantClient(host, port=port)
        self._embeddings = OllamaEmbeddings(model=embedding_model_name)

        self._ensure_collection_exists()

        self._vector_store = QdrantVectorStore(
            client=self._client,
            collection_name=self._collection_name,
            embedding=self._embeddings,
            distance=Distance.COSINE,
        )

    async def recreate_collection(self) -> None:
        if self._client.collection_exists(self._collection_name):
            self._client.delete_collection(self._collection_name)

        self._client.create_collection(
            collection_name=self._collection_name,
            vectors_config=VectorParams(
                size=self._vector_size,
                distance=Distance.COSINE,
            ),
        )

        self._vector_store = QdrantVectorStore(
            client=self._client,
            collection_name=self._collection_name,
            embedding=self._embeddings,
            distance=Distance.COSINE,
        )

        logger.info(
            "qdrant_collection_recreated",
            collection=self._collection_name,
        )

    async def add_document(
        self,
        content: str,
        source: str | None = None,
    ) -> None:
        if not content.strip():
            return

        self._ensure_collection_exists()

        metadata = {}
        if source is not None:
            metadata["source"] = source

        document = Document(
            page_content=content.strip(),
            metadata=metadata,
        )

        document_id = self._build_document_id(source or content)

        self._vector_store.add_documents([document], ids=[document_id])

        logger.info(
            "document_added_to_index",
            source=source,
            collection=self._collection_name,
        )

    async def search(
        self,
        query: str,
        limit: int = 1,
        score_threshold: float = 0.62,
    ) -> IndexedDocument | None:
        try:
            self._ensure_collection_exists()

            results = self._vector_store.similarity_search_with_score(
                query,
                k=limit,
                score_threshold=score_threshold,
            )

            if not results:
                logger.info("document_index_search_not_found", query=query)
                return None

            document, score = results[0]

            return IndexedDocument(
                content=document.page_content,
                source=document.metadata.get("source"),
                score=score,
            )

        except Exception as exc:
            logger.error(
                "document_index_search_failed",
                query=query,
                error=str(exc),
                exc_info=True,
            )
            return None
    
    async def search_many(
        self,
        query: str,
        limit: int = 5,
        score_threshold: float = 0.0,
    ) -> list[IndexedDocument]:
        try:
            self._ensure_collection_exists()

            results = self._vector_store.similarity_search_with_score(
                query,
                k=limit,
                score_threshold=score_threshold,
            )

            indexed = [
                IndexedDocument(
                    content=document.page_content,
                    source=document.metadata.get("source"),
                    score=score,
                )
                for document, score in results
            ]

            logger.info(
                "document_index_search_many_finished",
                query=query,
                results=[
                    {
                        "source": item.source,
                        "score": item.score,
                        "preview": f"{item.content[:80]}...",
                    }
                    for item in indexed
                ],
            )

            return indexed

        except Exception as exc:
            logger.error(
                "document_index_search_many_failed",
                query=query,
                error=str(exc),
                exc_info=True,
            )
        return []

    def _ensure_collection_exists(self) -> None:
        if self._client.collection_exists(self._collection_name):
            return

        self._client.create_collection(
            collection_name=self._collection_name,
            vectors_config=VectorParams(
                size=self._vector_size,
                distance=Distance.COSINE,
            ),
        )

        logger.info(
            "qdrant_collection_created",
            collection=self._collection_name,
        )

    def _build_document_id(self, value: str) -> str:
        return str(uuid.uuid5(uuid.NAMESPACE_URL, value))
