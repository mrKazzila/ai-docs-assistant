from ai_docs_assistant.application.interfaces.document_index import IndexedDocument


class SearchRelevancePolicy:
    MIN_SCORE = 0.62

    DOMAIN_TOKENS = {
        "profile": ("профил", "profile"),
        "users": ("пользовател", "user", "юзер"),
        "tasks": ("задач", "task", "todo"),
    }

    ACTION_TOKENS = {
        "delete": ("удал", "delete", "remove"),
        "create": ("созда", "добав", "create", "post"),
        "update": ("обнов", "измен", "update", "patch"),
        "get": ("получ", "список", "get", "read"),
    }

    def is_relevant(
        self,
        query: str,
        selected: IndexedDocument | None,
    ) -> bool:
        if selected is None:
            return False

        if selected.score < self.MIN_SCORE:
            return False

        normalized_query = query.lower()
        normalized_document = self._normalize_document(selected)

        expected_domain = self._detect_expected(
            normalized_query,
            self.DOMAIN_TOKENS,
        )
        expected_action = self._detect_expected(
            normalized_query,
            self.ACTION_TOKENS,
        )

        if expected_domain is not None and expected_domain not in normalized_document:
            return False

        if expected_action is not None and expected_action not in normalized_document:
            return False

        return True

    def _normalize_document(self, document: IndexedDocument) -> str:
        content = document.content.lower()
        source = (document.source or "").lower()

        markers: list[str] = []

        if "/profile" in content or "profile" in source:
            markers.append("profile")

        if "/users" in content or "user" in source:
            markers.append("users")

        if "/tasks" in content or "task" in source:
            markers.append("tasks")

        if content.startswith("### get"):
            markers.append("get")

        if content.startswith("### post"):
            markers.append("create")

        if content.startswith("### delete"):
            markers.append("delete")

        if content.startswith(("### patch", "### put")):
            markers.append("update")

        return " ".join(markers)

    def _detect_expected(
        self,
        query: str,
        token_groups: dict[str, tuple[str, ...]],
    ) -> str | None:
        for marker, tokens in token_groups.items():
            if any(token in query for token in tokens):
                return marker

        return None
