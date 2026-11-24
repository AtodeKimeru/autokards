"""Integration tests for the flashcard generation API endpoint."""

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_returns_400_with_validation_error_when_text_is_empty() -> None:
    # Arrange
    payload = {"text": ""}

    # Act
    response = client.post("/api/v1/flashcards/generate", json=payload)

    # Assert
    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert body["error"]["message"] == "Readable study text is required"
    assert body["error"]["details"] == []
    assert ".apkg" not in response.text


def test_returns_400_with_validation_error_when_text_is_whitespace_only() -> None:
    # Arrange
    payload = {"text": "   \t\n  "}

    # Act
    response = client.post("/api/v1/flashcards/generate", json=payload)

    # Assert
    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert body["error"]["message"] == "Readable study text is required"
    assert ".apkg" not in response.text


def test_returns_200_with_data_cards_when_generation_succeeds() -> None:
    # Arrange
    payload = {"text": "The capital of France is Paris."}

    # Act
    response = client.post("/api/v1/flashcards/generate", json=payload)

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert isinstance(body["data"]["cards"], list)
    assert len(body["data"]["cards"]) >= 1
    for card in body["data"]["cards"]:
        assert card["front"].strip()
        assert card["back"].strip()
    assert "error" not in body
    assert ".apkg" not in response.text


def test_returns_422_when_provider_limit_exceeded() -> None:
    # Arrange
    payload = {"text": "The capital of France is Paris."}

    from src.application.services.generate_flashcards_use_case import (
        GenerateFlashcardsUseCase,
    )
    from src.domain.exceptions import ProviderLimitExceededError
    from src.infrastructure.composition import get_flashcards_use_case

    class LimitGenerator:
        async def generate(self, study_text):
            raise ProviderLimitExceededError("Input exceeds provider limit")

    app.dependency_overrides[get_flashcards_use_case] = lambda: GenerateFlashcardsUseCase(
        generator=LimitGenerator()
    )

    try:
        # Act
        response = client.post("/api/v1/flashcards/generate", json=payload)

        # Assert
        assert response.status_code == 422
        body = response.json()
        assert body["success"] is False
        assert body["error"]["code"] == "INPUT_EXCEEDS_PROVIDER_LIMIT"
        assert ".apkg" not in response.text
    finally:
        del app.dependency_overrides[get_flashcards_use_case]


def test_returns_502_when_provider_fails() -> None:
    # Arrange
    payload = {"text": "The capital of France is Paris."}

    from src.application.services.generate_flashcards_use_case import (
        GenerateFlashcardsUseCase,
    )
    from src.domain.exceptions import GenerationError
    from src.infrastructure.composition import get_flashcards_use_case

    class FailingGenerator:
        async def generate(self, study_text):
            raise GenerationError("Provider failure")

    app.dependency_overrides[get_flashcards_use_case] = lambda: GenerateFlashcardsUseCase(
        generator=FailingGenerator()
    )

    try:
        # Act
        response = client.post("/api/v1/flashcards/generate", json=payload)

        # Assert
        assert response.status_code == 502
        body = response.json()
        assert body["success"] is False
        assert body["error"]["code"] == "GENERATION_ERROR"
        # Ensure no Python traceback is exposed in response
        assert "Traceback" not in response.text
        assert "File " not in response.text
        assert ".apkg" not in response.text
    finally:
        del app.dependency_overrides[get_flashcards_use_case]


def test_returns_413_with_input_too_large_when_text_exceeds_byte_limit() -> None:
    """Excessively large input should be rejected with 413 and no provider call."""
    from unittest.mock import patch

    # Set a small limit to trigger the validation error
    oversized_text = "x" * (10 * 1024)  # 10 KiB
    payload = {"text": oversized_text}

    # Patch the settings.max_input_bytes in the schema module
    with patch(
        "src.application.schemas.generate_flashcards.settings.max_input_bytes",
        100,
    ):
        # Act
        response = client.post("/api/v1/flashcards/generate", json=payload)

        # Assert - should get 413 because the validator caught oversized input
        assert response.status_code == 413
        body = response.json()
        assert body["success"] is False
        assert body["error"]["code"] == "INPUT_TOO_LARGE"
        assert body["error"]["message"] == "Input exceeds byte limit"
        assert "details" in body["error"]
        assert isinstance(body["error"]["details"], list)
        assert len(body["error"]["details"]) >= 1
        detail = body["error"]["details"][0]
        assert "limit_bytes" in detail
        assert "received_bytes" in detail
        # These values come from InputTooLargeError and the patched max_input_bytes
        assert detail["limit_bytes"] == 100
        assert detail["received_bytes"] == len(oversized_text.encode("utf-8"))
        assert ".apkg" not in response.text


def test_returns_200_when_text_is_at_byte_ceiling() -> None:
    """Text exactly at the byte limit should succeed."""
    from src.config import settings

    # Generate text exactly at the limit - the JSON payload will be slightly larger
    # but that's OK - we're testing that exact-size text passes the validator
    text_at_limit = "x" * settings.max_input_bytes
    payload = {"text": text_at_limit}

    # Act
    response = client.post("/api/v1/flashcards/generate", json=payload)

    # Assert - should succeed (provider will be called)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert ".apkg" not in response.text


def test_returns_200_with_typed_flashcard_schema() -> None:
    """OpenAPI response should reference typed front/back schema."""
    payload = {"text": "The capital of France is Paris."}

    # Act
    response = client.post("/api/v1/flashcards/generate", json=payload)

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert isinstance(body["data"]["cards"], list)
    for card in body["data"]["cards"]:
        assert "front" in card
        assert "back" in card
        assert isinstance(card["front"], str)
        assert isinstance(card["back"], str)


def test_returns_422_with_invalid_request_for_missing_field() -> None:
    """Missing or unknown request field should return 422 INVALID_REQUEST without echoing input."""
    # Act - missing 'text' field
    response = client.post("/api/v1/flashcards/generate", json={})

    # Assert
    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "INVALID_REQUEST"
    # Response should not echo back the submitted input
    response_text = response.text
    assert "text" not in response_text or "field required" in body["error"]["message"].lower()
