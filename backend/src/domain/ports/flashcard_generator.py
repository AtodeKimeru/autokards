"""FlashcardGenerator domain port.

A provider-agnostic abstraction that turns validated study text into one or
more flashcards. The use case depends on this abstraction, not on a concrete
LLM provider.
"""

from typing import Protocol

from src.domain.models.flashcard import Flashcard
from src.domain.models.study_text import StudyText


class FlashcardGenerator(Protocol):
    """Port for generating flashcards from validated study text."""

    async def generate(self, study_text: StudyText) -> tuple[Flashcard, ...]:
        """Generate one or more flashcards from validated study text.

        Raises :class:`GenerationError` (or a subclass such as
        :class:`ProviderLimitExceededError` or
        :class:`InvalidGeneratorOutputError`) when generation cannot succeed.

        Args:
            study_text: Study text that passed input validation.

        Returns:
            A non-empty tuple of flashcards.
        """
        ...  # pragma: no cover
