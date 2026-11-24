"""Deterministic StubGenerator infrastructure adapter.

A test double and offline fallback for flashcard generation that does not
require network access or LLM credentials. Selected when ``LLM_PROVIDER=stub``.
Output is deterministic for a given input so curl verification and unit tests
are reproducible offline.
"""

from src.domain.exceptions import ValidationError
from src.domain.models.flashcard import Flashcard
from src.domain.models.study_text import StudyText
from src.domain.ports.flashcard_generator import FlashcardGenerator


class StubGenerator(FlashcardGenerator):
    """Deterministic stub adapter returning known flashcards without network."""

    def __init__(self, default_cards: list[Flashcard] | None = None) -> None:
        self._default_cards = default_cards or [
            Flashcard(
                front="What is the main topic of the text?",
                back="The text covers the submitted study content.",
            ),
            Flashcard(
                front="Name one key detail from the text.",
                back="A key detail is present in the submitted study content.",
            ),
        ]

    async def generate(self, study_text: StudyText) -> tuple[Flashcard, ...]:
        """Generate deterministic flashcards from study text.

        Args:
            study_text: Study text that passed input validation.

        Returns:
            A non-empty tuple of flashcards.
        """
        if not study_text.value or not study_text.value.strip():
            raise ValidationError("Readable study text is required")

        # Deterministic output derived solely from the input text length so the
        # same text always yields the same cards, offline and without network.
        card_count = max(1, min(len(self._default_cards), len(study_text.value) // 10 + 1))
        return tuple(self._default_cards[:card_count])
