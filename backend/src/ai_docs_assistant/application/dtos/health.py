from dataclasses import dataclass


@dataclass(frozen=True)
class HealthcheckResult:
    status: str
    checks: dict[str, bool]
