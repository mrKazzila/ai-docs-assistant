from ai_docs_assistant.application.interfaces import (
    generation_job_repository as generation_job_repository_interfaces,
)
from ai_docs_assistant.application.interfaces.document_index import (
    DocumentIndex,
)
from ai_docs_assistant.application.interfaces.document_storage import (
    DocumentStorage,
)
from ai_docs_assistant.application.interfaces.generation_job_queue import (
    GenerationJobQueue,
)
from ai_docs_assistant.application.interfaces.health_checker import (
    HealthChecker,
)
from ai_docs_assistant.application.use_cases.create_generation_job import (
    CreateGenerationJobUseCase,
)
from ai_docs_assistant.application.use_cases.get_generation_job import (
    GetGenerationJobUseCase,
)
from ai_docs_assistant.application.use_cases.healthcheck import (
    HealthcheckUseCase,
)
from ai_docs_assistant.application.use_cases.search_docs import (
    SearchDocsUseCase,
)
from ai_docs_assistant.config.settings.base import Settings
from ai_docs_assistant.infrastructure.health import (
    HttpHealthChecker,
    HttpProbe,
)


def create_document_index(settings: Settings) -> DocumentIndex:
    # Import lazily so the API container does not pull vector-store extras
    # before this dependency is actually needed.
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


def create_create_generation_job_use_case(
    repository: generation_job_repository_interfaces.GenerationJobRepository,
    queue: GenerationJobQueue,
) -> CreateGenerationJobUseCase:
    return CreateGenerationJobUseCase(
        repository=repository,
        queue=queue,
    )


def create_get_generation_job_use_case(
    repository: generation_job_repository_interfaces.GenerationJobRepository,
) -> GetGenerationJobUseCase:
    return GetGenerationJobUseCase(repository=repository)


def create_search_docs_use_case(
    document_index: DocumentIndex,
) -> SearchDocsUseCase:
    return SearchDocsUseCase(document_index=document_index)


def create_healthcheck_use_case(
    health_checker: HealthChecker,
) -> HealthcheckUseCase:
    return HealthcheckUseCase(checker=health_checker)
