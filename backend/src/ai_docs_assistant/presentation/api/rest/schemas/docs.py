from pydantic import BaseModel


class GenerateDocumentRequest(BaseModel):
    query: str


class GenerateDocumentResponse(BaseModel):
    success: bool
    message: str
    content: str | None = None
    file_path: str | None = None


class SearchDocumentRequest(BaseModel):
    query: str


class SearchDocumentResponse(BaseModel):
    found: bool
    content: str | None = None
    message: str | None = None
