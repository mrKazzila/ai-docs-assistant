__all__ = ("Settings",)

from typing import final

from pydantic import Field

from ai_docs_assistant.config.settings._base_settings import BaseAppSettings
from ai_docs_assistant.config.settings.app import AppSettings
from ai_docs_assistant.config.settings.ollama import OllamaSettings
from ai_docs_assistant.config.settings.qdrant import QdrantSettings


@final
class Settings(BaseAppSettings):
    app: AppSettings = Field(default_factory=AppSettings)
    qdrant: QdrantSettings = Field(default_factory=QdrantSettings)
    ollama: OllamaSettings = Field(default_factory=OllamaSettings)

    @property
    def log_level(self) -> str:
        return self.app.log_level

    @property
    def debug(self) -> bool:
        return self.app.debug

    @property
    def qdrant_url(self) -> str:
        return self.qdrant.url

    @property
    def ollama_url(self) -> str:
        return self.ollama.url
