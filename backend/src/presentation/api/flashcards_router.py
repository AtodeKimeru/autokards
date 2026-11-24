"""Flashcard generation API routes."""

from typing import Annotated

from fastapi import APIRouter, Depends

from src.application.schemas.generate_flashcards import GenerateFlashcardsRequest
from src.application.services.generate_flashcards_use_case import (
    GenerateFlashcardsUseCase,
    get_flashcards_use_case,
)

router = APIRouter(prefix="/api/v1/flashcards", tags=["flashcards"])


@router.post("/generate", status_code=200)
async def generate_flashcards(
    request: GenerateFlashcardsRequest,
    use_case: Annotated[GenerateFlashcardsUseCase, Depends(get_flashcards_use_case)],
) -> dict[str, object]:
    """Generate flashcards from submitted study text.

    Invalid (empty or whitespace-only) input raises ``ValidationError``
    which the global exception handler maps to HTTP 400. Generation
    failures map to HTTP 422 (provider limit) or HTTP 502 (provider
    error). No ``.apkg`` download is produced or offered.
    """
    cards = await use_case.execute(request)
    return {
        "success": True,
        "data": {
            "cards": [{"front": card.front, "back": card.back} for card in cards],
        },
        "message": "Flashcards generated",
    }
