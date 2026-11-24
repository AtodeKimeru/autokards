"""StudyText domain value object.

A self-validating immutable value object representing readable study text
submitted at the generation entry point (FR-3).
"""

from dataclasses import dataclass

from src.domain.exceptions import ValidationError


@dataclass(frozen=True)
class StudyText:
    """Study text that is guaranteed to be readable on construction.

    Raises :class:`ValidationError` when the text is empty or contains
    only whitespace characters.
    """

    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValidationError("Readable study text is required")
