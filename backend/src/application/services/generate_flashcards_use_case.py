"""Application use case for generating flashcards from study text.

Validates the submitted study text at the generation entry point (FR-3) and
delegates flashcard generation to an injected ``FlashcardGenerator`` (FR-4).
The application layer stays free of provider coupling; production wiring is
done in ``main.py`` (composition root).
"""

from src.application.schemas.generate_flashcards import GenerateFlashcardsRequest
from src.domain.exceptions import GenerationError
from src.domain.models.flashcard import Flashcard
from src.domain.models.flashcard_set import FlashcardSet
from src.domain.models.study_text import StudyText
from src.domain.ports.flashcard_generator import FlashcardGenerator


class GenerateFlashcardsUseCase:
    """Orchestrates input validation before flashcard generation."""

    def __init__(self, generator: FlashcardGenerator | None = None) -> None:
        self._generator = generator

    async def execute(self, request: GenerateFlashcardsRequest) -> tuple[Flashcard, ...]:
        """Validate the request and generate flashcards from the text.

        Raises :class:`ValidationError` when the text is empty or
        whitespace-only, stopping the flow before any generation work.
        Raises :class:`GenerationError` when the generator returns zero cards,
        returns invalid output, or fails.
        """
        study_text = StudyText(value=request.text)
        return await self._generate(study_text)

    async def _generate(self, study_text: StudyText) -> tuple[Flashcard, ...]:
        generator = self._generator or self._resolve_default_generator()
        cards = await generator.generate(study_text)
        if not cards:
            raise GenerationError("No flashcards were generated from the input")
        return FlashcardSet(cards=cards).cards

    def _resolve_default_generator(self) -> FlashcardGenerator:
        """Resolve the generator configured for the current environment."""
        raise NotImplementedError(
            "Default generator resolution is handled in main.py wiring; "
            "inject a generator for tests or configure LLM_PROVIDER in production."
        )


def get_flashcards_use_case() -> GenerateFlashcardsUseCase:
    """Dependency factory providing a ``GenerateFlashcardsUseCase`` instance.

    Production wiring is done in ``main.py`` which resolves ``LLM_PROVIDER``
    before constructing the use case. Tests construct
    ``GenerateFlashcardsUseCase(generator=...)`` directly with a fake.
    """
    return GenerateFlashcardsUseCase()
