from functools import lru_cache

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
from ai_docs_assistant.config.dependencies.facade import (
    ApiDependencies,
    create_api_dependencies,
)
from ai_docs_assistant.config.settings.base import Settings


def get_create_generation_job_use_case() -> CreateGenerationJobUseCase:
    return _get_api_dependencies().create_generation_job_use_case


def get_get_generation_job_use_case() -> GetGenerationJobUseCase:
    return _get_api_dependencies().get_generation_job_use_case


def get_search_docs_use_case() -> SearchDocsUseCase:
    return _get_api_dependencies().search_docs_use_case


def get_healthcheck_use_case() -> HealthcheckUseCase:
    return _get_api_dependencies().healthcheck_use_case


@lru_cache
def _get_api_dependencies() -> ApiDependencies:
    return create_api_dependencies(settings=Settings())
