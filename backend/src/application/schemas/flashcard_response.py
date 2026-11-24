"""Pydantic response schemas for flashcard generation API."""

from pydantic import BaseModel, Field


class FlashcardResponse(BaseModel):
    """A single flashcard with front and back fields."""

    front: str = Field(..., description="Front side of the flashcard")
    back: str = Field(..., description="Back side of the flashcard")


class FlashcardDataResponse(BaseModel):
    """Data wrapper containing the list of generated flashcards."""

    cards: list[FlashcardResponse] = Field(..., description="List of generated flashcards")


class GenerateFlashcardsSuccessResponse(BaseModel):
    """Successful response for flashcard generation."""

    success: bool = Field(..., description="Always true for successful responses")
    data: FlashcardDataResponse = Field(..., description="Generated flashcards data")
    message: str = Field(
        default="Flashcards generated",
        description="Human-readable success message",
    )


class ErrorDetail(BaseModel):
    """Error detail object for error responses."""

    limit_bytes: int | None = Field(default=None, description="Byte limit when applicable")
    received_bytes: int | None = Field(
        default=None, description="Received byte count when applicable"
    )


class ErrorResponse(BaseModel):
    """Standard error response envelope."""

    success: bool = Field(..., description="Always false for error responses")
    error: "ErrorEnvelope" = Field(..., description="Error details")


class ErrorEnvelope(BaseModel):
    """Error envelope containing code, message, and optional details."""

    message: str = Field(..., description="Human-readable error message")
    code: str = Field(..., description="Machine-readable error code")
    details: list[ErrorDetail] = Field(default_factory=list, description="Additional error details")


ErrorResponse.model_rebuild()
