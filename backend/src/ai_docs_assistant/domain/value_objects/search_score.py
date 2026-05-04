from dataclasses import dataclass


@dataclass(frozen=True)
class SearchScore:
    value: float

    def is_above_or_equal(self, threshold: float) -> bool:
        return self.value >= threshold
