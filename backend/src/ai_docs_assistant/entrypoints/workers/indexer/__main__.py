import asyncio

import structlog

from ai_docs_assistant.config.dependencies.facade import (
    create_indexer_dependencies,
)
from ai_docs_assistant.config.settings.base import Settings
from ai_docs_assistant.config.settings.logger import (
    LoggingConfig,
    setup_logging,
)
from ai_docs_assistant.entrypoints.workers.indexer.cli import parse_args

logger = structlog.get_logger(__name__)


async def main() -> None:
    args = parse_args()

    logger.info(
        "indexer_started",
        recreate=not args.no_recreate,
    )

    dependencies = create_indexer_dependencies(
        settings=Settings(),
    )

    await dependencies.use_case.execute(
        recreate=not args.no_recreate,
    )

    logger.info("indexer_finished")


if __name__ == "__main__":
    setup_logging(
        config=LoggingConfig(
            level="INFO",
            renderer="console",
            enable_diagnostics=False,
            use_utc_timestamps=True,
        ),
    )
    asyncio.run(main())
