from ai_docs_assistant.application.dtos.generation_jobs import (
    GetGenerationJobDTO,
    GetGenerationJobResultDTO,
)
from ai_docs_assistant.application.interfaces.generation_job_repository import (
    GenerationJobRepository,
)


class GetGenerationJobUseCase:
    def __init__(self, repository: GenerationJobRepository) -> None:
        self._repository = repository

    async def execute(
        self,
        query: GetGenerationJobDTO,
    ) -> GetGenerationJobResultDTO | None:
        job = await self._repository.get_by_id(query.job_id)

        if job is None:
            return None

        return GetGenerationJobResultDTO(
            job_id=job.id,
            query=job.query,
            status=job.status,
            content=job.content,
            file_path=job.file_path,
            error_message=job.error_message,
        )
