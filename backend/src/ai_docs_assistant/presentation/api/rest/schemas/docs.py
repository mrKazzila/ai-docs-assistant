from pydantic import BaseModel


class SGenerateDocumentRequest(BaseModel):
    query: str


class SGenerateDocumentResponse(BaseModel):
    success: bool
    message: str
    content: str | None = None
    file_path: str | None = None


class SSearchDocumentRequest(BaseModel):
    query: str


class SSearchDocumentResponse(BaseModel):
    found: bool
    content: str | None = None
    message: str | None = None
