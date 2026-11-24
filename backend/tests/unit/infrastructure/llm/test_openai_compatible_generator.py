"""Unit tests for the OpenAI-compatible LLM flashcard generator adapter."""

import httpx
import pytest

from src.domain.exceptions import (
    GenerationError,
    InvalidGeneratorOutputError,
    ProviderLimitExceededError,
)
from src.domain.models.flashcard import Flashcard
from src.domain.models.study_text import StudyText
from src.infrastructure.llm.openai_compatible_generator import OpenAICompatibleGenerator


class TestOpenAICompatibleGenerator:
    async def test_returns_cards_when_provider_returns_valid_json_array(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Arrange
        generator = OpenAICompatibleGenerator(
            base_url="http://example.com/v1",
            api_key="test-key",
            model="gpt-4o-mini",
            timeout_seconds=5,
        )
        monkeypatch.setattr(
            httpx.AsyncClient,
            "post",
            self._mock_post_success,
        )

        # Act
        cards = await generator.generate(StudyText(value="The capital of France is Paris."))

        # Assert
        assert cards == (Flashcard(front="Q1", back="A1"),)

    async def test_raises_invalid_generator_output_when_json_is_malformed(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Arrange
        generator = OpenAICompatibleGenerator(
            base_url="http://example.com/v1",
            api_key="test-key",
            model="gpt-4o-mini",
            timeout_seconds=5,
        )
        monkeypatch.setattr(httpx.AsyncClient, "post", self._mock_post_malformed_json)

        # Act & Assert
        with pytest.raises(InvalidGeneratorOutputError):
            await generator.generate(StudyText(value="The capital of France is Paris."))

    async def test_raises_invalid_generator_output_when_cards_are_empty(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Arrange
        generator = OpenAICompatibleGenerator(
            base_url="http://example.com/v1",
            api_key="test-key",
            model="gpt-4o-mini",
            timeout_seconds=5,
        )
        monkeypatch.setattr(httpx.AsyncClient, "post", self._mock_post_empty_cards)

        # Act & Assert
        with pytest.raises(InvalidGeneratorOutputError):
            await generator.generate(StudyText(value="The capital of France is Paris."))

    async def test_raises_invalid_generator_output_when_field_is_empty(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Arrange
        generator = OpenAICompatibleGenerator(
            base_url="http://example.com/v1",
            api_key="test-key",
            model="gpt-4o-mini",
            timeout_seconds=5,
        )
        monkeypatch.setattr(httpx.AsyncClient, "post", self._mock_post_empty_field)

        # Act & Assert
        with pytest.raises(InvalidGeneratorOutputError):
            await generator.generate(StudyText(value="The capital of France is Paris."))

    async def test_raises_provider_limit_exceeded_when_422(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Arrange
        generator = OpenAICompatibleGenerator(
            base_url="http://example.com/v1",
            api_key="test-key",
            model="gpt-4o-mini",
            timeout_seconds=5,
        )
        monkeypatch.setattr(httpx.AsyncClient, "post", self._mock_post_422)

        # Act & Assert
        with pytest.raises(ProviderLimitExceededError):
            await generator.generate(StudyText(value="The capital of France is Paris."))

    async def test_raises_generation_error_when_http_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Arrange
        generator = OpenAICompatibleGenerator(
            base_url="http://example.com/v1",
            api_key="test-key",
            model="gpt-4o-mini",
            timeout_seconds=5,
        )
        monkeypatch.setattr(httpx.AsyncClient, "post", self._mock_post_500)

        # Act & Assert
        with pytest.raises(GenerationError):
            await generator.generate(StudyText(value="The capital of France is Paris."))

    async def test_raises_generation_error_when_timeout(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Arrange
        generator = OpenAICompatibleGenerator(
            base_url="http://example.com/v1",
            api_key="test-key",
            model="gpt-4o-mini",
            timeout_seconds=5,
        )
        monkeypatch.setattr(httpx.AsyncClient, "post", self._mock_post_timeout)

        # Act & Assert
        with pytest.raises(GenerationError):
            await generator.generate(StudyText(value="The capital of France is Paris."))

    # --- mock helpers ---

    async def _mock_post_success(self, url: str, **kwargs: object) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": '[{"front": "Q1", "back": "A1"}]',
                        },
                    },
                ],
            },
        )

    async def _mock_post_malformed_json(self, url: str, **kwargs: object) -> httpx.Response:
        return httpx.Response(200, json={"choices": [{"message": {"content": "not json"}}]})

    async def _mock_post_empty_cards(self, url: str, **kwargs: object) -> httpx.Response:
        return httpx.Response(200, json={"choices": [{"message": {"content": "[]"}}]})

    async def _mock_post_empty_field(self, url: str, **kwargs: object) -> httpx.Response:
        return httpx.Response(
            200, json={"choices": [{"message": {"content": '[{"front": "", "back": "A1"}]'}}]}
        )

    async def _mock_post_422(self, url: str, **kwargs: object) -> httpx.Response:
        return httpx.Response(422, json={"error": {"message": "input too long"}})

    async def _mock_post_500(self, url: str, **kwargs: object) -> httpx.Response:
        return httpx.Response(500, json={"error": {"message": "server error"}})

    async def _mock_post_timeout(self, url: str, **kwargs: object) -> httpx.Response:
        raise httpx.TimeoutException("request timed out")
