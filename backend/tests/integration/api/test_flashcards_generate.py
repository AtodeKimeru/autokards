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
        get_flashcards_use_case,
    )
    from src.domain.exceptions import ProviderLimitExceededError

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
        app.dependency_overrides.clear()


def test_returns_502_when_provider_fails() -> None:
    # Arrange
    payload = {"text": "The capital of France is Paris."}

    from src.application.services.generate_flashcards_use_case import (
        GenerateFlashcardsUseCase,
        get_flashcards_use_case,
    )
    from src.domain.exceptions import GenerationError

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
        assert "stack" not in response.text.lower()
        assert ".apkg" not in response.text
    finally:
        app.dependency_overrides.clear()
