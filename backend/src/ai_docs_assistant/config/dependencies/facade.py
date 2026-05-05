from dataclasses import dataclass

from ai_docs_assistant.application.interfaces.generation_job_queue import (
    GenerationJobQueue,
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
from ai_docs_assistant.application.use_cases.initialize_knowledge_base import (
    InitializeKnowledgeBaseUseCase,
)
from ai_docs_assistant.application.use_cases.process_generation_job import (
    ProcessGenerationJobUseCase,
)
from ai_docs_assistant.application.use_cases.search_docs import (
    SearchDocsUseCase,
)
from ai_docs_assistant.config.dependencies.api import (
    create_create_generation_job_use_case,
    create_document_index,
    create_get_generation_job_use_case,
    create_health_checker,
    create_healthcheck_use_case,
    create_search_docs_use_case,
)
from ai_docs_assistant.config.dependencies.common import (
    create_document_filename_policy,
    create_document_policy,
    create_document_storage,
    create_generation_job_queue,
    create_generation_job_repository,
    create_http_probe,
    create_redis,
)
from ai_docs_assistant.config.dependencies.generation import (
    create_document_generator,
    create_document_index as create_generation_document_index,
    create_generate_docs_use_case,
    create_process_generation_job_use_case,
)
from ai_docs_assistant.config.dependencies.indexer import (
    create_document_index as create_indexer_document_index,
    create_initialize_knowledge_base_use_case,
)
from ai_docs_assistant.config.settings.base import Settings


@dataclass(frozen=True)
class ApiDependencies:
    create_generation_job_use_case: CreateGenerationJobUseCase
    get_generation_job_use_case: GetGenerationJobUseCase
    search_docs_use_case: SearchDocsUseCase
    healthcheck_use_case: HealthcheckUseCase


@dataclass(frozen=True)
class IndexerDependencies:
    use_case: InitializeKnowledgeBaseUseCase


@dataclass(frozen=True)
class GenerationWorkerDependencies:
    queue: GenerationJobQueue
    process_generation_job_use_case: ProcessGenerationJobUseCase


def create_api_dependencies(settings: Settings) -> ApiDependencies:
    redis = create_redis(settings)
    repository = create_generation_job_repository(
        settings=settings,
        redis=redis,
    )
    queue = create_generation_job_queue(
        settings=settings,
        redis=redis,
    )

    storage = create_document_storage(settings)
    document_index = create_document_index(settings)
    http_probe = create_http_probe()

    health_checker = create_health_checker(
        settings=settings,
        storage=storage,
        document_index=document_index,
        http_probe=http_probe,
    )

    return ApiDependencies(
        create_generation_job_use_case=create_create_generation_job_use_case(
            repository=repository,
            queue=queue,
        ),
        get_generation_job_use_case=create_get_generation_job_use_case(
            repository=repository,
        ),
        search_docs_use_case=create_search_docs_use_case(
            document_index=document_index,
        ),
        healthcheck_use_case=create_healthcheck_use_case(
            health_checker=health_checker,
        ),
    )


def create_indexer_dependencies(settings: Settings) -> IndexerDependencies:
    storage = create_document_storage(settings)
    document_index = create_indexer_document_index(settings)

    return IndexerDependencies(
        use_case=create_initialize_knowledge_base_use_case(
            storage=storage,
            document_index=document_index,
        ),
    )


def create_generation_worker_dependencies(
    settings: Settings,
) -> GenerationWorkerDependencies:
    redis = create_redis(settings)

    repository = create_generation_job_repository(
        settings=settings,
        redis=redis,
    )
    queue = create_generation_job_queue(
        settings=settings,
        redis=redis,
    )

    storage = create_document_storage(settings)
    document_index = create_generation_document_index(settings)
    generator = create_document_generator(settings)

    document_policy = create_document_policy()
    filename_policy = create_document_filename_policy()

    generate_docs_use_case = create_generate_docs_use_case(
        generator=generator,
        storage=storage,
        document_index=document_index,
        document_policy=document_policy,
        filename_policy=filename_policy,
    )

    process_generation_job_use_case = create_process_generation_job_use_case(
        repository=repository,
        generate_docs_use_case=generate_docs_use_case,
    )

    return GenerationWorkerDependencies(
        queue=queue,
        process_generation_job_use_case=process_generation_job_use_case,
    )
