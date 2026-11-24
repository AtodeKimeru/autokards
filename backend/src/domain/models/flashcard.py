"""Flashcard domain value object.

A self-validating immutable value object representing a single front/back
flashcard. The Front and Back fields are independent and both must be
non-empty (AC-1, AC-2).
"""

from dataclasses import dataclass

from src.domain.exceptions import ValidationError


@dataclass(frozen=True)
class Flashcard:
    """A single flashcard with separate, non-empty Front and Back fields.

    Raises :class:`ValidationError` when either field is empty or contains
    only whitespace characters.
    """

    front: str
    back: str

    def __post_init__(self) -> None:
        if not self.front or not self.front.strip():
            raise ValidationError("Front must be non-empty")
        if not self.back or not self.back.strip():
            raise ValidationError("Back must be non-empty")
