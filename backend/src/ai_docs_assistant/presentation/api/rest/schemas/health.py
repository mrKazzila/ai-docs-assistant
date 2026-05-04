from pydantic import BaseModel


class HealthcheckResponse(BaseModel):
    status: str
    checks: dict[str, bool]
