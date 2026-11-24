"""Application use case for generating flashcards from study text.

Validates the submitted study text at the generation entry point and
stops the flow without invoking generation when input is invalid
(FR-3). Valid input proceeds by returning the validated ``StudyText``
for downstream flashcard generation (FR-4, separate change).
"""

from src.application.schemas.generate_flashcards import GenerateFlashcardsRequest
from src.domain.models.study_text import StudyText


def get_flashcards_use_case() -> "GenerateFlashcardsUseCase":
    """Dependency factory providing a ``GenerateFlashcardsUseCase`` instance."""
    return GenerateFlashcardsUseCase()


class GenerateFlashcardsUseCase:
    """Orchestrates input validation before flashcard generation."""

    def execute(self, request: GenerateFlashcardsRequest) -> StudyText:
        """Validate the request and return study text ready for generation.

        Raises :class:`ValidationError` when the text is empty or
        whitespace-only, stopping the flow before any generation work.
        """
        study_text = StudyText(value=request.text)
        return study_text
