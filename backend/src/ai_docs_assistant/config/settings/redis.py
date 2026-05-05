__all__ = ("RedisSettings",)

from pydantic import Field

from ai_docs_assistant.config.settings._base_settings import BaseAppSettings


class RedisSettings(BaseAppSettings):

    host: str = Field("127.0.0.1", validation_alias="REDIS_HOST")
    port: int = Field(6379, validation_alias="REDIS_PORT")
    db: int = Field(
        0,
        validation_alias="REDIS_DB",
    )
    ttl_seconds: int = Field(
        86400,
        validation_alias="REDIS_GENERATION_JOB_TTL_SECONDS",
    )
    queue_name: str = Field(
        "generation:queue",
        validation_alias="REDIS_GENERATION_QUEUE_NAME",
    )
