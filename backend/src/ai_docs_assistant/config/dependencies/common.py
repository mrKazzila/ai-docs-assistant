from pathlib import Path

from redis.asyncio import Redis

from ai_docs_assistant.application.interfaces import (
    generation_job_repository as generation_job_repository_interfaces,
)
from ai_docs_assistant.application.interfaces.document_storage import (
    DocumentStorage,
)
from ai_docs_assistant.application.interfaces.generation_job_queue import (
    GenerationJobQueue,
)
from ai_docs_assistant.config.settings.base import Settings
from ai_docs_assistant.domain.services.document_filename_policy import (
    DocumentFilenamePolicy,
)
from ai_docs_assistant.domain.services.document_policy import DocumentPolicy
from ai_docs_assistant.infrastructure.health import HttpProbe
from ai_docs_assistant.infrastructure.redis.client import create_redis_client
from ai_docs_assistant.infrastructure.redis.generation_job_queue import (
    RedisListGenerationJobQueue,
)
from ai_docs_assistant.infrastructure.redis.generation_job_repository import (
    RedisGenerationJobRepository,
)
from ai_docs_assistant.infrastructure.storage import FilesystemDocumentStorage


def create_document_storage(settings: Settings) -> DocumentStorage:
    return FilesystemDocumentStorage(
        docs_dir=Path(settings.app.docs_dir),
    )


def create_document_policy() -> DocumentPolicy:
    return DocumentPolicy(similarity_threshold=0.75)


def create_document_filename_policy() -> DocumentFilenamePolicy:
    return DocumentFilenamePolicy()


def create_http_probe() -> HttpProbe:
    return HttpProbe(timeout=3.0)


def create_redis(settings: Settings) -> Redis:
    return create_redis_client(
        host=settings.redis.host,
        port=settings.redis.port,
        db=settings.redis.db,
        decode_responses=True,
    )


def create_generation_job_repository(
    settings: Settings,
    redis: Redis,
) -> generation_job_repository_interfaces.GenerationJobRepository:
    return RedisGenerationJobRepository(
        redis=redis,
        ttl_seconds=settings.redis.ttl_seconds,
    )


def create_generation_job_queue(
    settings: Settings,
    redis: Redis,
) -> GenerationJobQueue:
    return RedisListGenerationJobQueue(
        redis=redis,
        queue_name=settings.redis.queue_name,
    )
