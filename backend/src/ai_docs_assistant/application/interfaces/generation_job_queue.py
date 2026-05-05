from typing import Protocol
from uuid import UUID


class GenerationJobQueue(Protocol):
    async def enqueue(self, job_id: UUID) -> None: ...

    async def dequeue(self, timeout: int = 5) -> UUID | None: ...
