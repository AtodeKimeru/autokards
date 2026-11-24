"""Flashcard generation API routes."""

from typing import Annotated

from fastapi import APIRouter, Depends

from src.application.schemas.flashcard_response import (
    FlashcardDataResponse,
    FlashcardResponse,
    GenerateFlashcardsSuccessResponse,
)
from src.application.schemas.generate_flashcards import GenerateFlashcardsRequest
from src.application.services.generate_flashcards_use_case import (
    GenerateFlashcardsUseCase,
)
from src.domain.models.flashcard import Flashcard
from src.infrastructure.composition import get_flashcards_use_case

router = APIRouter(prefix="/api/v1/flashcards", tags=["flashcards"])


@router.post(
    "/generate",
    status_code=200,
    response_model=GenerateFlashcardsSuccessResponse,
)
async def generate_flashcards(
    request: GenerateFlashcardsRequest,
    use_case: Annotated[GenerateFlashcardsUseCase, Depends(get_flashcards_use_case)],
) -> GenerateFlashcardsSuccessResponse:
    """Generate flashcards from submitted study text.

    Invalid (empty or whitespace-only) input raises ``ValidationError``
    which the global exception handler maps to HTTP 400. Generation
    failures map to HTTP 422 (provider limit) or HTTP 502 (provider
    error). Input exceeding ``MAX_INPUT_BYTES`` raises ``InputTooLargeError``
    which maps to HTTP 413.
    """
    cards: tuple[Flashcard, ...] = await use_case.execute(request)
    flashcard_data = FlashcardDataResponse(
        cards=[FlashcardResponse(front=card.front, back=card.back) for card in cards]
    )
    return GenerateFlashcardsSuccessResponse(
        success=True,
        data=flashcard_data,
        message="Flashcards generated",
    )
