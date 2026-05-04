from dataclasses import dataclass

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
from ai_docs_assistant.config.dependencies.container import (
    create_document_filename_policy,
    create_document_generator,
    create_document_index,
    create_document_policy,
    create_document_storage,
    create_generate_docs_use_case,
    create_health_checker,
    create_healthcheck_use_case,
    create_http_probe,
    create_initialize_knowledge_base_use_case,
    create_search_docs_use_case,
)
from ai_docs_assistant.config.settings.base import Settings


@dataclass(frozen=True)
class ApiDependencies:
    generate_docs_use_case: GenerateDocsUseCase
    search_docs_use_case: SearchDocsUseCase
    healthcheck_use_case: HealthcheckUseCase


@dataclass(frozen=True)
class IndexerDependencies:
    use_case: InitializeKnowledgeBaseUseCase


def create_api_dependencies(
    settings: Settings,
) -> ApiDependencies:
    storage = create_document_storage(settings)
    document_index = create_document_index(settings)
    generator = create_document_generator(settings)

    document_policy = create_document_policy()
    filename_policy = create_document_filename_policy()
    http_probe = create_http_probe()

    health_checker = create_health_checker(
        settings=settings,
        storage=storage,
        document_index=document_index,
        http_probe=http_probe,
    )

    return ApiDependencies(
        generate_docs_use_case=create_generate_docs_use_case(
            generator=generator,
            storage=storage,
            document_index=document_index,
            document_policy=document_policy,
            filename_policy=filename_policy,
        ),
        search_docs_use_case=create_search_docs_use_case(
            document_index=document_index,
        ),
        healthcheck_use_case=create_healthcheck_use_case(
            health_checker=health_checker,
        ),
    )


def create_indexer_dependencies(
    settings: Settings,
) -> IndexerDependencies:
    storage = create_document_storage(settings)
    document_index = create_document_index(settings)

    return IndexerDependencies(
        use_case=create_initialize_knowledge_base_use_case(
            storage=storage,
            document_index=document_index,
        ),
    )
