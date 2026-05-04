__all__ = ("QdrantSettings",)

from pydantic import Field

from ai_docs_assistant.config.settings._base_settings import BaseAppSettings


class QdrantSettings(BaseAppSettings):
    host: str = Field("localhost", validation_alias="QDRANT_HOST")
    port: int = Field(6333, validation_alias="QDRANT_PORT")
    collection_name: str = Field(
        "api_docs",
        validation_alias="QDRANT_COLLECTION_NAME",
    )
    embedding_model_name: str = Field(
        "mxbai-embed-large",
        validation_alias="EMBEDDING_MODEL_NAME",
    )
    vector_size: int = Field(1024, validation_alias="VECTOR_SIZE")

    @property
    def url(self):
        return f"http://{self.host}:{self.port}"
