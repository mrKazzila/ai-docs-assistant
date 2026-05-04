__all__  = (
    "ROUTERS",
)

from ai_docs_assistant.presentation.api.rest.routers.docs import (
    router as docs_router,
)
from ai_docs_assistant.presentation.api.rest.routers.healthcheck import (
    healthcheck as healthcheck_router,
)

ROUTERS = (
    docs_router,
    healthcheck_router,
)
