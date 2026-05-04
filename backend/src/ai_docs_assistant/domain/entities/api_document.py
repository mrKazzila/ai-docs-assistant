from dataclasses import dataclass
from datetime import datetime
from typing import NewType

DocumentId = NewType("DocumentId", str)


@dataclass(frozen=True)
class ApiDocument:
    id: DocumentId
    title: str
    content: str
    filename: str
    created_at: datetime | None = None
