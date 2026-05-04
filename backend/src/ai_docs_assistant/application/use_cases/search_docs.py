from ai_docs_assistant.application.dtos.documents import (
    SearchDocumentQuery,
    SearchDocumentResult,
)
from ai_docs_assistant.application.interfaces.document_index import (
    DocumentIndex,
)


class SearchDocsUseCase:
    def __init__(self, document_index: DocumentIndex) -> None:
        self._document_index = document_index

    async def execute(
        self,
        query: SearchDocumentQuery,
    ) -> SearchDocumentResult:
        result = await self._document_index.search(query.query)

        if result is None:
            return SearchDocumentResult(
                found=False,
                content=None,
                message=(
                    "Документация не найдена. "
                    "Используйте /generate для создания новой."
                ),
            )

        return SearchDocumentResult(
            found=True,
            content=result.content,
            message=None,
        )
