from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class IndexedDocument:
    content: str
    source: str | None
    score: float


class DocumentIndex(Protocol):
    async def recreate_collection(self) -> None:
        """Recreate vector collection."""

    async def add_document(
        self,
        content: str,
        source: str | None = None,
    ) -> None:
        """Add document content to vector index."""

    async def search(
        self,
        query: str,
        limit: int = 1,
        score_threshold: float = 0.62,
    ) -> IndexedDocument | None:
        """Search relevant indexed document."""

    async def search_many(
        self,
        query: str,
        limit: int = 5,
        score_threshold: float = 0.0,
    ) -> list[IndexedDocument]:
        """Search many relevant indexed document."""

