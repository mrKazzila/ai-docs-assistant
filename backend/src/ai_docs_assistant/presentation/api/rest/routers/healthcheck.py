from fastapi import APIRouter, Depends

from ai_docs_assistant.application.use_cases.healthcheck import (
    HealthcheckUseCase,
)
from ai_docs_assistant.presentation.api.rest.dependencies import (
    get_healthcheck_use_case,
)
from ai_docs_assistant.presentation.api.rest.schemas.health import (
    HealthcheckResponse,
)

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthcheckResponse)
async def healthcheck(
    use_case: HealthcheckUseCase = Depends(get_healthcheck_use_case),
) -> HealthcheckResponse:
    result = await use_case.execute()

    return HealthcheckResponse(
        status=result.status,
        checks=result.checks,
    )
