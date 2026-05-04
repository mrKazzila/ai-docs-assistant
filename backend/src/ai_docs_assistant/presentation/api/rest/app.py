from fastapi import FastAPI

from ai_docs_assistant.presentation.api.rest.routers import ROUTERS


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Docs Assistant",
        description=(
            "Local FastAPI service for "
            "API documentation generation "
            "and semantic search."
        ),
        version="0.1.0",
    )

    [app.include_router(router) for router in ROUTERS]

    return app
