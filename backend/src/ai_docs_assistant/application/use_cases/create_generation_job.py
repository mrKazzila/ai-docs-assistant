from datetime import UTC, datetime
from uuid import uuid4

from ai_docs_assistant.application.dtos.generation_jobs import (
    CreateGenerationJobDTO,
    CreateGenerationJobResultDTO,
)
from ai_docs_assistant.application.interfaces.generation_job_queue import (
    GenerationJobQueue,
)
from ai_docs_assistant.application.interfaces.generation_job_repository import (
    GenerationJobRepository,
)
from ai_docs_assistant.domain.entities.generation_job import GenerationJob
from ai_docs_assistant.domain.enums.generation_job_status import (
    GenerationJobStatus,
)


class CreateGenerationJobUseCase:
    def __init__(
        self,
        repository: GenerationJobRepository,
        queue: GenerationJobQueue,
    ) -> None:
        self._repository = repository
        self._queue = queue

    async def execute(
        self,
        command: CreateGenerationJobDTO,
    ) -> CreateGenerationJobResultDTO:
        now = datetime.now(UTC)

        job = GenerationJob(
            id=uuid4(),
            query=command.query,
            status=GenerationJobStatus.PENDING,
            created_at=now,
            updated_at=now,
        )

        await self._repository.add(job)
        await self._queue.enqueue(job.id)

        return CreateGenerationJobResultDTO(
            job_id=job.id,
            status=job.status,
        )
