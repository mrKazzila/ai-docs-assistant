from dataclasses import dataclass
from uuid import UUID

from ai_docs_assistant.domain.enums.generation_job_status import (
    GenerationJobStatus,
)


@dataclass(frozen=True)
class CreateGenerationJobDTO:
    query: str


@dataclass(frozen=True)
class CreateGenerationJobResultDTO:
    job_id: UUID
    status: GenerationJobStatus


@dataclass(frozen=True)
class GetGenerationJobDTO:
    job_id: UUID


@dataclass(frozen=True)
class GetGenerationJobResultDTO:
    job_id: UUID
    query: str
    status: GenerationJobStatus
    content: str | None = None
    file_path: str | None = None
    error_message: str | None = None
