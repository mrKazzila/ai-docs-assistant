from pathlib import Path

from ai_docs_assistant.application.interfaces.document_generator import (
    DocumentGenerator,
)
from ai_docs_assistant.application.interfaces.document_index import (
    DocumentIndex,
)
from ai_docs_assistant.application.interfaces.document_storage import (
    DocumentStorage,
)
from ai_docs_assistant.application.interfaces.health_checker import (
    HealthChecker,
)
from ai_docs_assistant.application.use_cases.generate_docs import (
    GenerateDocsUseCase,
)
from ai_docs_assistant.application.use_cases.healthcheck import (
    HealthcheckUseCase,
)
from ai_docs_assistant.application.use_cases.initialize_knowledge_base import (
    InitializeKnowledgeBaseUseCase,
)
from ai_docs_assistant.application.use_cases.search_docs import (
    SearchDocsUseCase,
)
from ai_docs_assistant.config.settings.base import Settings
from ai_docs_assistant.domain.services.document_filename_policy import (
    DocumentFilenamePolicy,
)
from ai_docs_assistant.domain.services.document_policy import DocumentPolicy
from ai_docs_assistant.infrastructure.agents.crewai_document_generator import (
    CrewAIDocumentGenerator,
)
from ai_docs_assistant.infrastructure.health import (
    HttpHealthChecker,
    HttpProbe,
)
from ai_docs_assistant.infrastructure.storage import (
    FilesystemDocumentStorage,
)
from ai_docs_assistant.infrastructure.vector_store import (
    QdrantDocumentIndex,
)


def create_document_storage(settings: Settings) -> DocumentStorage:
    return FilesystemDocumentStorage(
        docs_dir=Path(settings.app.docs_dir),
    )


def create_document_index(settings: Settings) -> DocumentIndex:
    return QdrantDocumentIndex(
        host=settings.qdrant.host,
        port=settings.qdrant.port,
        collection_name=settings.qdrant.collection_name,
        embedding_model_name=settings.qdrant.embedding_model_name,
        vector_size=settings.qdrant.vector_size,
    )


def create_document_generator(settings: Settings) -> DocumentGenerator:
    return CrewAIDocumentGenerator(
        model=settings.ollama.model,
        base_url=settings.ollama.url,
        api_key=settings.ollama.api_key,
        temperature=0.0,
        timeout=60.0,
        max_tokens=300,
    )


def create_http_probe() -> HttpProbe:
    return HttpProbe(timeout=3.0)


def create_health_checker(
    settings: Settings,
    storage: DocumentStorage,
    document_index: DocumentIndex,
    http_probe: HttpProbe,
) -> HealthChecker:
    return HttpHealthChecker(
        qdrant_url=settings.qdrant.url,
        ollama_url=settings.ollama.url,
        storage=storage,
        document_index=document_index,
        http_probe=http_probe,
    )


def create_document_policy() -> DocumentPolicy:
    return DocumentPolicy(similarity_threshold=0.75)


def create_document_filename_policy() -> DocumentFilenamePolicy:
    return DocumentFilenamePolicy()


def create_generate_docs_use_case(
    generator: DocumentGenerator,
    storage: DocumentStorage,
    document_index: DocumentIndex,
    document_policy: DocumentPolicy,
    filename_policy: DocumentFilenamePolicy,
) -> GenerateDocsUseCase:
    return GenerateDocsUseCase(
        generator=generator,
        storage=storage,
        document_index=document_index,
        document_policy=document_policy,
        filename_policy=filename_policy,
    )


def create_search_docs_use_case(
    document_index: DocumentIndex,
) -> SearchDocsUseCase:
    return SearchDocsUseCase(document_index=document_index)


def create_healthcheck_use_case(
    health_checker: HealthChecker,
) -> HealthcheckUseCase:
    return HealthcheckUseCase(checker=health_checker)


def create_initialize_knowledge_base_use_case(
    storage: DocumentStorage,
    document_index: DocumentIndex,
) -> InitializeKnowledgeBaseUseCase:
    return InitializeKnowledgeBaseUseCase(
        storage=storage,
        document_index=document_index,
    )
