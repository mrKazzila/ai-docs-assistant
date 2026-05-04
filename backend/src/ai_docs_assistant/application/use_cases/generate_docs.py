from ai_docs_assistant.application.dtos.documents import (
    GenerateDocumentCommand,
    GenerateDocumentResult,
)
from ai_docs_assistant.application.interfaces.document_generator import (
    DocumentGenerator,
)
from ai_docs_assistant.application.interfaces.document_index import (
    DocumentIndex,
)
from ai_docs_assistant.application.interfaces.document_storage import (
    DocumentStorage,
)
from ai_docs_assistant.domain.services.document_filename_policy import (
    DocumentFilenamePolicy,
)
from ai_docs_assistant.domain.services.document_policy import DocumentPolicy


class GenerateDocsUseCase:
    def __init__(
        self,
        generator: DocumentGenerator,
        storage: DocumentStorage,
        document_index: DocumentIndex,
        document_policy: DocumentPolicy,
        filename_policy: DocumentFilenamePolicy,
    ) -> None:
        self._generator = generator
        self._storage = storage
        self._document_index = document_index
        self._document_policy = document_policy
        self._filename_policy = filename_policy

    async def execute(
        self,
        command: GenerateDocumentCommand,
    ) -> GenerateDocumentResult:
        existing = await self._document_index.search(
            query=command.query,
            score_threshold=self._document_policy.similarity_threshold,
        )

        if existing is not None:
            return GenerateDocumentResult(
                success=True,
                message="Похожая документация уже существует.",
                content=existing.content,
                file_path=existing.source,
            )

        content = await self._generator.generate(command.query)

        if content is None:
            return GenerateDocumentResult(
                success=False,
                message="Ошибка генерации или валидации документа.",
            )

        if not self._document_policy.is_valid_content(content):
            return GenerateDocumentResult(
                success=False,
                message=(
                    "Сгенерированный документ не прошёл доменную валидацию."
                ),
                content=content,
            )

        filename = self._filename_policy.build_filename(command.query)

        file_path = await self._storage.save_unique(
            preferred_filename=filename,
            content=content,
        )

        await self._document_index.add_document(
            content=content,
            source=file_path,
        )

        return GenerateDocumentResult(
            success=True,
            message="Документ успешно создан и сохранён.",
            content=content,
            file_path=file_path,
        )
