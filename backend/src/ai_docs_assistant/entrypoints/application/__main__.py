import uvicorn

from ai_docs_assistant.config.settings.logger import (
    LoggingConfig,
    setup_logging,
)
from ai_docs_assistant.presentation.api.rest.app import create_app

setup_logging(
    config=LoggingConfig(
        level="INFO",
        renderer="console",
        enable_diagnostics=False,
        use_utc_timestamps=True,
    ),
)

app = create_app()


def main() -> None:
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_config=None,
        access_log=True,
    )


if __name__ == "__main__":
    main()
