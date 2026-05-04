__all__ = ("AppSettings",)

from typing import Literal

from pydantic import Field
from pathlib import Path

from ai_docs_assistant.config.settings._base_settings import BaseAppSettings


class AppSettings(BaseAppSettings):

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    debug: bool = Field(False, validation_alias="DEBUG")
    docs_dir: Path = Path("docs")
