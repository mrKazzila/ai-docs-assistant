from uuid import UUID

from redis.asyncio import Redis

from ai_docs_assistant.application.interfaces.generation_job_queue import (
    GenerationJobQueue,
)


class RedisListGenerationJobQueue(GenerationJobQueue):
    def __init__(
        self,
        redis: Redis,
        queue_name: str = "generation:queue",
    ) -> None:
        self._redis = redis
        self._queue_name = queue_name

    async def enqueue(self, job_id: UUID) -> None:
        await self._redis.lpush(self._queue_name, str(job_id))

    async def dequeue(self, timeout: int = 5) -> UUID | None:
        result = await self._redis.brpop(self._queue_name, timeout=timeout)

        if result is None:
            return None

        _, raw_job_id = result
        return UUID(raw_job_id)
