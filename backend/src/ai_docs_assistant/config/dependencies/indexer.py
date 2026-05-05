from ai_docs_assistant.application.interfaces.document_index import (
    DocumentIndex,
)
from ai_docs_assistant.application.interfaces.document_storage import (
    DocumentStorage,
)
from ai_docs_assistant.application.use_cases.initialize_knowledge_base import (
    InitializeKnowledgeBaseUseCase,
)
from ai_docs_assistant.config.settings.base import Settings


def create_document_index(settings: Settings) -> DocumentIndex:
    # Import lazily so indexer-only dependencies stay isolated from lighter
    # service runtimes during module import.
    from ai_docs_assistant.infrastructure.vector_store import (
        QdrantDocumentIndex,
    )  # noqa: PLC0415

    return QdrantDocumentIndex(
        host=settings.qdrant.host,
        port=settings.qdrant.port,
        collection_name=settings.qdrant.collection_name,
        embedding_model_name=settings.qdrant.embedding_model_name,
        vector_size=settings.qdrant.vector_size,
    )


def create_initialize_knowledge_base_use_case(
    storage: DocumentStorage,
    document_index: DocumentIndex,
) -> InitializeKnowledgeBaseUseCase:
    return InitializeKnowledgeBaseUseCase(
        storage=storage,
        document_index=document_index,
    )
