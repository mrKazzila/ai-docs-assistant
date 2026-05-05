from datetime import UTC, datetime
from uuid import UUID

from redis.asyncio import Redis

from ai_docs_assistant.application.interfaces.generation_job_repository import (
    GenerationJobRepository,
)
from ai_docs_assistant.domain.entities.generation_job import GenerationJob
from ai_docs_assistant.domain.enums.generation_job_status import (
    GenerationJobStatus,
)


class RedisGenerationJobRepository(GenerationJobRepository):
    def __init__(self, redis: Redis, ttl_seconds: int = 86400) -> None:
        self._redis = redis
        self._ttl_seconds = ttl_seconds

    async def add(self, job: GenerationJob) -> None:
        key = self._build_key(job.id)

        await self._redis.hset(
            key,
            mapping=self._to_mapping(job),
        )
        await self._redis.expire(key, self._ttl_seconds)

    async def get_by_id(self, job_id: UUID) -> GenerationJob | None:
        data = await self._redis.hgetall(self._build_key(job_id))

        if not data:
            return None

        return self._from_mapping(data)

    async def update(self, job: GenerationJob) -> None:
        key = self._build_key(job.id)

        await self._redis.hset(
            key,
            mapping=self._to_mapping(job),
        )
        await self._redis.expire(key, self._ttl_seconds)

    def _build_key(self, job_id: UUID) -> str:
        return f"generation:job:{job_id}"

    def _to_mapping(self, job: GenerationJob) -> dict[str, str]:
        return {
            "id": str(job.id),
            "query": job.query,
            "status": job.status.value,
            "content": job.content or "",
            "file_path": job.file_path or "",
            "error_message": job.error_message or "",
            "created_at": self._format_dt(job.created_at),
            "updated_at": self._format_dt(job.updated_at),
        }

    def _from_mapping(self, data: dict[str, str]) -> GenerationJob:
        return GenerationJob(
            id=UUID(data["id"]),
            query=data["query"],
            status=GenerationJobStatus(data["status"]),
            content=data.get("content") or None,
            file_path=data.get("file_path") or None,
            error_message=data.get("error_message") or None,
            created_at=self._parse_dt(data.get("created_at")),
            updated_at=self._parse_dt(data.get("updated_at")),
        )

    def _format_dt(self, value: datetime | None) -> str:
        if value is None:
            return ""

        return value.isoformat()

    def _parse_dt(self, value: str | None) -> datetime | None:
        if not value:
            return None

        parsed = datetime.fromisoformat(value)

        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=UTC)

        return parsed
