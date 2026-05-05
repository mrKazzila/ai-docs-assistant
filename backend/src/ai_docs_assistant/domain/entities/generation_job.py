from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from ai_docs_assistant.domain.enums.generation_job_status import (
    GenerationJobStatus,
)


@dataclass(frozen=True)
class GenerationJob:
    id: UUID
    query: str
    status: GenerationJobStatus
    content: str | None = None
    file_path: str | None = None
    error_message: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
