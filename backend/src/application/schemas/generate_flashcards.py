"""Pydantic request schema for flashcard generation input."""

from pydantic import BaseModel, Field, field_validator

from src.config import settings
from src.domain.exceptions import InputTooLargeError


class GenerateFlashcardsRequest(BaseModel):
    """Request body for generating flashcards from study text.

    Carries the submitted `text` that the domain layer will validate
    before generation proceeds. Enforces a byte ceiling to prevent
    oversized inputs that would fail at the provider level.
    """

    text: str = Field(..., description="Study text used to generate flashcards")

    @field_validator("text")
    @classmethod
    def _validate_byte_length(cls, v: str) -> str:
        """Check that text does not exceed the configured byte limit.

        Returns the text unchanged if valid, raises ``InputTooLargeError`` otherwise
        which will be mapped to HTTP 413 by the exception handler.
        """
        byte_length = len(v.encode("utf-8"))
        if byte_length > settings.max_input_bytes:
            raise InputTooLargeError(
                limit_bytes=settings.max_input_bytes,
                received_bytes=byte_length,
            )
        return v
