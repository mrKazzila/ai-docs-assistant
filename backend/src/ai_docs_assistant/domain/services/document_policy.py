class DocumentPolicy:
    def __init__(self, similarity_threshold: float = 0.75) -> None:
        self.similarity_threshold = similarity_threshold

    def is_valid_content(self, content: str) -> bool:
        stripped = content.strip()

        if not stripped:
            return False

        return stripped.startswith("###")
