from ai_docs_assistant.application.interfaces.document_index import (
    DocumentIndex,
)
from ai_docs_assistant.application.interfaces.document_storage import (
    DocumentStorage,
)


class InitializeKnowledgeBaseUseCase:
    def __init__(
        self,
        storage: DocumentStorage,
        document_index: DocumentIndex,
    ) -> None:
        self._storage = storage
        self._document_index = document_index

    async def execute(self, recreate: bool = True) -> None:
        if recreate:
            await self._document_index.recreate_collection()

        documents = await self._storage.read_all_markdown()

        for source, content in documents:
            await self._document_index.add_document(
                content=content,
                source=source,
            )
