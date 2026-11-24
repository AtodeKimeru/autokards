"""Flashcard generation API routes."""

from typing import Annotated

from fastapi import APIRouter, Depends

from src.application.schemas.generate_flashcards import GenerateFlashcardsRequest
from src.application.services.generate_flashcards_use_case import (
    GenerateFlashcardsUseCase,
    get_flashcards_use_case,
)

router = APIRouter(prefix="/api/v1/flashcards", tags=["flashcards"])


@router.post("/generate", status_code=202)
async def generate_flashcards(
    request: GenerateFlashcardsRequest,
    use_case: Annotated[GenerateFlashcardsUseCase, Depends(get_flashcards_use_case)],
) -> dict[str, object]:
    """Generate flashcards from submitted study text.

    Invalid (empty or whitespace-only) input raises ``ValidationError``
    which the global exception handler maps to HTTP 400. No ``.apkg``
    download is produced or offered for invalid input.
    """
    study_text = use_case.execute(request)
    return {
        "success": True,
        "data": {
            "text": study_text.value,
            "status": "accepted",
        },
        "message": "Flashcard generation accepted",
    }
