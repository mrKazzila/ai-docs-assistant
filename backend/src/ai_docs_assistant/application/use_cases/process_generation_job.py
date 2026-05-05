from dataclasses import replace
from datetime import UTC, datetime
from uuid import UUID

import structlog

from ai_docs_assistant.domain.entities.generation_job import GenerationJob
from ai_docs_assistant.application.dtos.documents import (
    GenerateDocumentDTO,
)
from ai_docs_assistant.application.interfaces.generation_job_repository import (
    GenerationJobRepository,
)
from ai_docs_assistant.application.use_cases.generate_docs import (
    GenerateDocsUseCase,
)
from ai_docs_assistant.domain.enums.generation_job_status import (
    GenerationJobStatus,
)

logger = structlog.get_logger(__name__)


class ProcessGenerationJobUseCase:
    def __init__(
        self,
        repository: GenerationJobRepository,
        generate_docs_use_case: GenerateDocsUseCase,
    ) -> None:
        self._repository = repository
        self._generate_docs_use_case = generate_docs_use_case

    async def execute(self, job_id: UUID) -> None:
        logger.info(
            "generation_job_processing_started",
            job_id=str(job_id),
        )

        job = await self._repository.get_by_id(job_id)

        if job is None:
            logger.warning(
                "generation_job_not_found",
                job_id=str(job_id),
            )
            return

        logger.info(
            "generation_job_loaded",
            job_id=str(job.id),
            query=job.query,
            status=job.status.value,
        )

        await self._mark_as_processing(job)

        try:
            logger.info(
                "generation_job_pipeline_started",
                job_id=str(job.id),
                query=job.query,
            )

            result = await self._generate_docs_use_case.execute(
                GenerateDocumentDTO(query=job.query),
            )

            if result.success:
                status = (
                    GenerationJobStatus.SKIPPED
                    if result.file_path is None
                    else GenerationJobStatus.COMPLETED
                )

                await self._repository.update(
                    replace(
                        job,
                        status=status,
                        content=result.content,
                        file_path=result.file_path,
                        error_message=None,
                        updated_at=datetime.now(UTC),
                    ),
                )

                logger.info(
                    "generation_job_pipeline_succeeded",
                    job_id=str(job.id),
                    status=status.value,
                    file_path=result.file_path,
                    content_length=len(result.content or ""),
                )
                return

            await self._repository.update(
                replace(
                    job,
                    status=GenerationJobStatus.FAILED,
                    content=result.content,
                    error_message=result.message,
                    updated_at=datetime.now(UTC),
                ),
            )

            logger.warning(
                "generation_job_pipeline_failed",
                job_id=str(job.id),
                status=GenerationJobStatus.FAILED.value,
                error_message=result.message,
                content_length=len(result.content or ""),
            )

        except Exception as exc:
            await self._repository.update(
                replace(
                    job,
                    status=GenerationJobStatus.FAILED,
                    error_message=str(exc),
                    updated_at=datetime.now(UTC),
                ),
            )

            logger.exception(
                "generation_job_processing_failed",
                job_id=str(job.id),
                error=str(exc),
            )

    async def _mark_as_processing(self, job: GenerationJob) -> None:
        await self._repository.update(
            replace(
                job,
                status=GenerationJobStatus.PROCESSING,
                updated_at=datetime.now(UTC),
            ),
        )

        logger.info(
            "generation_job_status_changed",
            job_id=str(job.id),
            status=GenerationJobStatus.PROCESSING.value,
        )
