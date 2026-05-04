from typing import Protocol


class DocumentStorage(Protocol):
    async def save_unique(self, preferred_filename: str, content: str) -> str:
        """Save document with unique filename and return saved path."""

    async def read_all_markdown(self) -> list[tuple[str, str]]:
        """Return list of (path, content)."""

    async def has_markdown_documents(self) -> bool:
        """Check that storage has at least one Markdown document."""
