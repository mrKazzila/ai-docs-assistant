from ai_docs_assistant.application.interfaces import (
    generation_job_repository as generation_job_repository_interfaces,
)
from ai_docs_assistant.application.interfaces.document_generator import (
    DocumentGenerator,
)
from ai_docs_assistant.application.interfaces.document_index import (
    DocumentIndex,
)
from ai_docs_assistant.application.interfaces.document_storage import (
    DocumentStorage,
)
from ai_docs_assistant.application.use_cases.generate_docs import (
    GenerateDocsUseCase,
)
from ai_docs_assistant.application.use_cases.process_generation_job import (
    ProcessGenerationJobUseCase,
)
from ai_docs_assistant.config.settings.base import Settings
from ai_docs_assistant.domain.services.document_filename_policy import (
    DocumentFilenamePolicy,
)
from ai_docs_assistant.domain.services.document_policy import DocumentPolicy


def create_document_index(settings: Settings) -> DocumentIndex:
    # Import lazily so generation-specific modules do not eagerly load the
    # vector-store stack when this module is imported elsewhere.
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


def create_document_generator(settings: Settings) -> DocumentGenerator:
    # Import lazily to keep heavy CrewAI dependencies out of API and indexer
    # runtimes until the generation worker actually constructs the generator.
    from ai_docs_assistant.infrastructure.agents import (
        CrewAIDocumentGenerator,
    )  # noqa: PLC0415

    return CrewAIDocumentGenerator(
        model=settings.ollama.model,
        base_url=settings.ollama.url,
        api_key=settings.ollama.api_key,
        temperature=0.0,
        timeout=60.0,
        max_tokens=300,
    )


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


def create_process_generation_job_use_case(
    repository: generation_job_repository_interfaces.GenerationJobRepository,
    generate_docs_use_case: GenerateDocsUseCase,
) -> ProcessGenerationJobUseCase:
    return ProcessGenerationJobUseCase(
        repository=repository,
        generate_docs_use_case=generate_docs_use_case,
    )
