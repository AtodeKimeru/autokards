"""Pydantic request schema for flashcard generation input."""

from pydantic import BaseModel, Field


class GenerateFlashcardsRequest(BaseModel):
    """Request body for generating flashcards from study text.

    Carries the submitted `text` that the domain layer will validate
    before generation proceeds.
    """

    text: str = Field(..., description="Study text used to generate flashcards")
