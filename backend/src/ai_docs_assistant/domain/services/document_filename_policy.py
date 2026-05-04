import re


class DocumentFilenamePolicy:
    ACTION_KEYWORDS = {
        "get": [
            "получ",
            "прочит",
            "профиль",
            "profile",
            "данные о",
            "информация о",
            "посмотреть",
        ],
        "create": ["созда", "добав", "новая", "новый", "сделать"],
        "delete": ["удали", "удал", "удаление", "уничтож", "remove"],
        "update": ["обнов", "измени", "измен", "статус", "редактируй", "edit"],
    }

    ENTITY_KEYWORDS = {
        "user": ["пользовател", "user", "юзер", "аккаунт"],
        "task": ["задач", "task", "дело", "todo"],
        "profile": ["профил", "profile", "личн", "инфо о себе"],
    }

    def build_base_name(self, query: str) -> str:
        text = query.lower()

        action = self._detect_action(text)
        entity = self._detect_entity(text)

        if entity:
            base_name = f"{action}_{entity}"
        else:
            base_name = action

        base_name = re.sub(r"[^a-z0-9_]", "", base_name)

        return base_name or "api_doc"

    def build_filename(self, query: str) -> str:
        return f"{self.build_base_name(query)}.md"

    def _detect_action(self, text: str) -> str:
        for action, keywords in self.ACTION_KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                return action

        return "api"

    def _detect_entity(self, text: str) -> str | None:
        for entity, keywords in self.ENTITY_KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                return entity

        return None
