from ai_docs_assistant.application.dtos.health import HealthcheckResult
from ai_docs_assistant.application.interfaces.health_checker import (
    HealthChecker,
)


class HealthcheckUseCase:
    def __init__(self, checker: HealthChecker) -> None:
        self._checker = checker

    async def execute(self) -> HealthcheckResult:
        checks = {
            "qdrant": await self._checker.check_qdrant(),
            "ollama": await self._checker.check_ollama(),
            "docs": await self._checker.check_docs(),
            "rag_canary": await self._checker.check_rag_canary(),
        }

        return HealthcheckResult(
            status="healthy" if all(checks.values()) else "unhealthy",
            checks=checks,
        )
