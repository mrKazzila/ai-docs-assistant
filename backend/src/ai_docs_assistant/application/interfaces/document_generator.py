from typing import Protocol


class DocumentGenerator(Protocol):
    async def generate(self, query: str) -> str | None:
        """Generate and validate Markdown documentation."""
