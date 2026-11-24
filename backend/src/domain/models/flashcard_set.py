"""FlashcardSet domain aggregate.

A collection of flashcards that guarantees at least one card is present,
representing the result of a successful generation (FR-4).
"""

from dataclasses import dataclass

from src.domain.exceptions import ValidationError
from src.domain.models.flashcard import Flashcard


@dataclass(frozen=True)
class FlashcardSet:
    """An aggregate of flashcards that guarantees at least one card.

    Raises :class:`ValidationError` when no cards are provided.
    """

    cards: tuple[Flashcard, ...]

    def __post_init__(self) -> None:
        if not self.cards:
            raise ValidationError("A flashcard set must contain at least one card")
