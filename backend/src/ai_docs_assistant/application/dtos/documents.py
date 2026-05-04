from dataclasses import dataclass


@dataclass(frozen=True)
class GenerateDocumentCommand:
    query: str


@dataclass(frozen=True)
class GenerateDocumentResult:
    success: bool
    message: str
    content: str | None = None
    file_path: str | None = None


@dataclass(frozen=True)
class SearchDocumentQuery:
    query: str


@dataclass(frozen=True)
class SearchDocumentResult:
    found: bool
    content: str | None = None
    message: str | None = None
