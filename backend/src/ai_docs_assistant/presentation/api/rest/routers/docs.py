from fastapi import APIRouter, Depends

from ai_docs_assistant.application.dtos.documents import (
    GenerateDocumentCommand,
    SearchDocumentQuery,
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
    GenerateDocumentRequest,
    GenerateDocumentResponse,
    SearchDocumentRequest,
    SearchDocumentResponse,
)

router = APIRouter(tags=["docs"])


@router.post("/generate", response_model=GenerateDocumentResponse)
async def generate_document(
    request: GenerateDocumentRequest,
    use_case: GenerateDocsUseCase = Depends(get_generate_docs_use_case),
) -> GenerateDocumentResponse:
    result = await use_case.execute(
        GenerateDocumentCommand(query=request.query),
    )

    return GenerateDocumentResponse(
        success=result.success,
        message=result.message,
        content=result.content,
        file_path=result.file_path,
    )


@router.post("/search", response_model=SearchDocumentResponse)
async def search_document(
    request: SearchDocumentRequest,
    use_case: SearchDocsUseCase = Depends(get_search_docs_use_case),
) -> SearchDocumentResponse:
    result = await use_case.execute(
        SearchDocumentQuery(query=request.query),
    )

    return SearchDocumentResponse(
        found=result.found,
        content=result.content,
        message=result.message,
    )
