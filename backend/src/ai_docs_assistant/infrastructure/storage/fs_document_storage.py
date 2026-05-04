from pathlib import Path

import structlog

from ai_docs_assistant.application.interfaces.document_storage import (
    DocumentStorage,
)

logger = structlog.get_logger(__name__)


class FilesystemDocumentStorage(DocumentStorage):
    def __init__(self, docs_dir: Path) -> None:
        self._docs_dir = docs_dir
        self._docs_dir.mkdir(parents=True, exist_ok=True)

    async def save_unique(self, preferred_filename: str, content: str) -> str:
        file_path = self._docs_dir / preferred_filename

        stem = file_path.stem
        suffix = file_path.suffix or ".md"

        counter = 1
        while file_path.exists():
            file_path = self._docs_dir / f"{stem}_{counter}{suffix}"
            counter += 1

        file_path.write_text(content.strip(), encoding="utf-8")

        logger.info("document_saved", file_path=str(file_path))
        return str(file_path)

    async def read_all_markdown(self) -> list[tuple[str, str]]:
        if not self._docs_dir.exists():
            return []

        documents: list[tuple[str, str]] = []

        for file_path in self._docs_dir.glob("*.md"):
            try:
                content = file_path.read_text(encoding="utf-8").strip()
            except OSError as exc:
                logger.error(
                    "document_read_failed",
                    file_path=str(file_path),
                    error=str(exc),
                )
                continue

            if content:
                documents.append((str(file_path), content))

        return documents

    async def has_markdown_documents(self) -> bool:
        return any(self._docs_dir.glob("*.md"))
