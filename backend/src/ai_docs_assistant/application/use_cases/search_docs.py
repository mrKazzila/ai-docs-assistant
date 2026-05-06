from ai_docs_assistant.application.dtos.documents import (
    SearchDocumentDTO,
    SearchedDocumentDTO,
)
from ai_docs_assistant.application.interfaces.document_index import (
    DocumentIndex,
)
from ai_docs_assistant.application.services.search_relevance_policy import (
    SearchRelevancePolicy,
)
from ai_docs_assistant.application.services.search_result_selector import (
    SearchResultSelector,
)


class SearchDocsUseCase:
    def __init__(
        self,
        document_index: DocumentIndex,
        result_selector: SearchResultSelector,
        relevance_policy: SearchRelevancePolicy,
    ) -> None:
        self._document_index = document_index
        self._result_selector = result_selector
        self._relevance_policy = relevance_policy

    async def execute(self, query: SearchDocumentDTO) -> SearchedDocumentDTO:
        candidates = await self._document_index.search_many(
            query=query.query,
            limit=5,
            score_threshold=0.0,
        )

        selected = self._result_selector.select(
            query=query.query,
            results=candidates,
        )

        if not self._relevance_policy.is_relevant(
            query=query.query,
            selected=selected,
        ):
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
            content=selected.content,
            message=None,
        )
