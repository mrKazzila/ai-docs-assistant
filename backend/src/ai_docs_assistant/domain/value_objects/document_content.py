from dataclasses import dataclass


@dataclass(frozen=True)
class DocumentContent:
    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("Document content cannot be empty")

    def as_string(self) -> str:
        return self.value
