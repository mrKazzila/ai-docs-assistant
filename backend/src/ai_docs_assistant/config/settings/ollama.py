__all__ = ("OllamaSettings",)

from pydantic import Field

from ai_docs_assistant.config.settings._base_settings import BaseAppSettings


class OllamaSettings(BaseAppSettings):

    api_key: str = Field("ollama", validation_alias="API_KEY")
    host: str = Field("127.0.0.1", validation_alias="OLLAMA_HOST")
    port: int = Field(11434, validation_alias="OLLAMA_PORT")
    model: str = Field(
        "ollama/my_api_docs",
        validation_alias="OLLAMA_MODEL",
    )

    @property
    def url(self):
        return f"http://{self.host}:{self.port}"
