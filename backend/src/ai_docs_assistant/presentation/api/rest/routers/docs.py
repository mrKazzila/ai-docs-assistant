from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from ai_docs_assistant.application.dtos.documents import SearchDocumentDTO
from ai_docs_assistant.application.dtos.generation_jobs import (
    CreateGenerationJobDTO,
    GetGenerationJobDTO,
)
from ai_docs_assistant.application.use_cases.create_generation_job import (
    CreateGenerationJobUseCase,
)
from ai_docs_assistant.application.use_cases.get_generation_job import (
    GetGenerationJobUseCase,
)
from ai_docs_assistant.application.use_cases.search_docs import (
    SearchDocsUseCase,
)
from ai_docs_assistant.presentation.api.rest.dependencies import (
    get_create_generation_job_use_case,
    get_get_generation_job_use_case,
    get_search_docs_use_case,
)
from ai_docs_assistant.presentation.api.rest.schemas.docs import (
    SCreateGenerationJobResponse,
    SGenerateDocumentRequest,
    SGenerationJobResponse,
    SSearchDocumentRequest,
    SSearchDocumentResponse,
)

router = APIRouter(tags=["docs"])


@router.post(
    path="/generate",
    status_code=status.HTTP_202_ACCEPTED,
)
async def create_generation_job(
    request: SGenerateDocumentRequest,
    use_case: Annotated[
        CreateGenerationJobUseCase,
        Depends(get_create_generation_job_use_case),
    ],
) -> SCreateGenerationJobResponse:
    result = await use_case.execute(
        CreateGenerationJobDTO(query=request.query),
    )

    return SCreateGenerationJobResponse(
        job_id=result.job_id,
        status=result.status,
    )


@router.get(path="/generate/{job_id}")
async def get_generation_job(
    job_id: UUID,
    use_case: Annotated[
        GetGenerationJobUseCase,
        Depends(get_get_generation_job_use_case),
    ],
) -> SGenerationJobResponse:
    result = await use_case.execute(
        GetGenerationJobDTO(job_id=job_id),
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generation job not found.",
        )

    return SGenerationJobResponse(
        job_id=result.job_id,
        query=result.query,
        status=result.status,
        content=result.content,
        file_path=result.file_path,
        error_message=result.error_message,
    )


@router.post(path="/search")
async def search_document(
    request: SSearchDocumentRequest,
    use_case: Annotated[
        SearchDocsUseCase,
        Depends(get_search_docs_use_case),
    ],
) -> SSearchDocumentResponse:
    result = await use_case.execute(
        SearchDocumentDTO(query=request.query),
    )

    return SSearchDocumentResponse(
        found=result.found,
        content=result.content,
        message=result.message,
    )
