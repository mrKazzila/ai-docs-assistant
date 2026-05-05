import asyncio
import signal
from uuid import UUID

import structlog

from ai_docs_assistant.config.dependencies.facade import (
    GenerationWorkerDependencies,
    create_generation_worker_dependencies,
)
from ai_docs_assistant.config.settings.base import Settings
from ai_docs_assistant.config.settings.logger import (
    LoggingConfig,
    setup_logging,
)

logger = structlog.get_logger(__name__)
QUEUE_DEQUEUE_TIMEOUT_SECONDS = 5


async def main() -> None:
    dependencies = _build_dependencies()
    stop_event = asyncio.Event()

    _register_shutdown_handlers(stop_event)

    await _run_worker(
        dependencies=dependencies,
        stop_event=stop_event,
    )


def _build_dependencies() -> GenerationWorkerDependencies:
    return create_generation_worker_dependencies(
        settings=Settings(),
    )


def _register_shutdown_handlers(stop_event: asyncio.Event) -> None:
    loop = asyncio.get_running_loop()

    def request_shutdown() -> None:
        logger.info("generation_worker_shutdown_requested")
        stop_event.set()

    loop.add_signal_handler(signal.SIGTERM, request_shutdown)
    loop.add_signal_handler(signal.SIGINT, request_shutdown)


async def _run_worker(
    dependencies: GenerationWorkerDependencies,
    stop_event: asyncio.Event,
) -> None:
    logger.info("generation_worker_started")

    while not stop_event.is_set():
        job_id = await dependencies.queue.dequeue(
            timeout=QUEUE_DEQUEUE_TIMEOUT_SECONDS,
        )

        if job_id is None:
            continue

        await _process_job(
            job_id=job_id,
            dependencies=dependencies,
        )

    logger.info("generation_worker_stopped")


async def _process_job(
    job_id: UUID,
    dependencies: GenerationWorkerDependencies,
) -> None:
    logger.info("generation_job_received", job_id=str(job_id))

    try:
        await dependencies.process_generation_job_use_case.execute(job_id)
    except Exception as exc:
        logger.exception(
            "generation_job_processing_failed",
            job_id=str(job_id),
            error=str(exc),
        )


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
