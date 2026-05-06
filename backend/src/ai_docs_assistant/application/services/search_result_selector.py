from ai_docs_assistant.application.interfaces.document_index import (
    IndexedDocument,
)


class SearchResultSelector:
    PROFILE_TOKENS = ("профил", "profile")
    TASK_TOKENS = ("задач", "task", "todo")
    USER_TOKENS = ("пользовател", "user", "юзер")

    def select(
        self,
        query: str,
        results: list[IndexedDocument],
    ) -> IndexedDocument | None:
        if not results:
            return None

        normalized_query = query.lower()

        preferred_path = self._detect_preferred_path(normalized_query)

        if preferred_path is not None:
            for result in results:
                content = result.content.lower()
                source = (result.source or "").lower()

                if preferred_path in content or preferred_path in source:
                    return result

        return results[0]

    def _detect_preferred_path(self, query: str) -> str | None:
        if any(token in query for token in self.PROFILE_TOKENS):
            return "profile"

        if any(token in query for token in self.TASK_TOKENS):
            return "task"

        if any(token in query for token in self.USER_TOKENS):
            return "user"

        return None
