from functools import lru_cache

from ai_docs_assistant.config.dependencies.facade import (
    ApiDependencies,
    create_api_dependencies,
)
from ai_docs_assistant.config.settings.base import Settings


@lru_cache
def get_api_dependencies() -> ApiDependencies:
    return create_api_dependencies(settings=Settings())


def get_generate_docs_use_case():
    return get_api_dependencies().generate_docs_use_case


def get_search_docs_use_case():
    return get_api_dependencies().search_docs_use_case


def get_healthcheck_use_case():
    return get_api_dependencies().healthcheck_use_case
