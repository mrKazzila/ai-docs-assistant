from ai_docs_assistant.application.dtos.documents import (
    SearchDocumentDTO,
    SearchedDocumentDTO,
)
from ai_docs_assistant.application.interfaces.document_index import (
    DocumentIndex,
)


class SearchDocsUseCase:
    def __init__(self, document_index: DocumentIndex) -> None:
        self._document_index = document_index

    async def execute(
        self,
        query: SearchDocumentDTO,
    ) -> SearchedDocumentDTO:
        result = await self._document_index.search(query.query)

        if result is None:
            return SearchedDocumentDTO(
                found=False,
                content=None,
                message=(
                    "Документация не найдена. "
                    "Используйте /generate для создания новой."
                ),
            )

        return SearchedDocumentDTO(
            found=True,
            content=result.content,
            message=None,
        )
