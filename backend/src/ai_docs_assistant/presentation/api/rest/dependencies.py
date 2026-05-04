from functools import lru_cache

import structlog

from ai_docs_assistant.config.dependencies.facade import (
    ApiDependencies,
    create_api_dependencies,
)
from ai_docs_assistant.config.settings.base import Settings

logger = structlog.get_logger(__name__)


def get_generate_docs_use_case():
    api_dependencies = _get_api_dependencies()
    logger.info("get_generate_docs_use_case", dep_id=id(api_dependencies))
    return api_dependencies.generate_docs_use_case


def get_search_docs_use_case():
    api_dependencies = _get_api_dependencies()
    logger.info("get_search_docs_use_case", dep_id=id(api_dependencies))
    return api_dependencies.search_docs_use_case


def get_healthcheck_use_case():
    api_dependencies = _get_api_dependencies()
    logger.info("get_healthcheck_use_case", dep_id=id(api_dependencies))
    return api_dependencies.healthcheck_use_case


@lru_cache
def _get_api_dependencies() -> ApiDependencies:
    api_dependencies = create_api_dependencies(settings=Settings())
    logger.info("_get_api_dependencies", dep_id=id(api_dependencies))
    return api_dependencies
