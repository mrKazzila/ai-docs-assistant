from enum import StrEnum, auto


class GenerationJobStatus(StrEnum):
    PENDING = auto()
    PROCESSING = auto()
    COMPLETED = auto()
    FAILED = auto()
    SKIPPED = auto()
