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


def test_proceeds_with_202_when_text_is_valid() -> None:
    # Arrange
    payload = {"text": "Review chapter 3"}

    # Act
    response = client.post("/api/v1/flashcards/generate", json=payload)

    # Assert
    assert response.status_code == 202
    body = response.json()
    assert body["success"] is True
    assert body["data"]["text"] == "Review chapter 3"
    assert body["data"]["status"] == "accepted"
