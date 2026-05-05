from typing import Protocol
from uuid import UUID

from ai_docs_assistant.domain.entities.generation_job import GenerationJob


class GenerationJobRepository(Protocol):
    async def add(self, job: GenerationJob) -> None: ...

    async def get_by_id(self, job_id: UUID) -> GenerationJob | None: ...

    async def update(self, job: GenerationJob) -> None: ...
