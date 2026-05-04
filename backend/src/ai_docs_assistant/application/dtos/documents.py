from dataclasses import dataclass


@dataclass(frozen=True)
class GenerateDocumentDTO:
    query: str


@dataclass(frozen=True)
class GeneratedDocumentDTO:
    success: bool
    message: str
    content: str | None = None
    file_path: str | None = None


@dataclass(frozen=True)
class SearchDocumentDTO:
    query: str


@dataclass(frozen=True)
class SearchedDocumentDTO:
    found: bool
    content: str | None = None
    message: str | None = None
