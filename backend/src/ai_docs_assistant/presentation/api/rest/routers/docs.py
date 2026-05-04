from typing import Annotated

from fastapi import APIRouter, Depends

from ai_docs_assistant.application.dtos.documents import (
    GenerateDocumentDTO,
    SearchDocumentDTO,
)
from ai_docs_assistant.application.use_cases.generate_docs import (
    GenerateDocsUseCase,
)
from ai_docs_assistant.application.use_cases.search_docs import (
    SearchDocsUseCase,
)
from ai_docs_assistant.presentation.api.rest.dependencies import (
    get_generate_docs_use_case,
    get_search_docs_use_case,
)
from ai_docs_assistant.presentation.api.rest.schemas.docs import (
    SGenerateDocumentRequest,
    SGenerateDocumentResponse,
    SSearchDocumentRequest,
    SSearchDocumentResponse,
)

router = APIRouter(tags=["docs"])


@router.post("/generate")
async def generate_document(
    request: SGenerateDocumentRequest,
    use_case: Annotated[
        GenerateDocsUseCase,
        Depends(get_generate_docs_use_case),
    ],
) -> SGenerateDocumentResponse:
    result = await use_case.execute(
        GenerateDocumentDTO(query=request.query),
    )

    return SGenerateDocumentResponse(
        success=result.success,
        message=result.message,
        content=result.content,
        file_path=result.file_path,
    )


@router.post("/search")
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
