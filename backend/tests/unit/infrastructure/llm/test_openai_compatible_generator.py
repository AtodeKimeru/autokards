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

    async def test_raises_provider_limit_exceeded_when_400_signals_context_overflow(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Arrange: OpenAI, OpenRouter, Ollama, and LM Studio report context-length
        # overflow as HTTP 400, not 422, so detection must not be 422-only.
        generator = OpenAICompatibleGenerator(
            base_url="http://example.com/v1",
            api_key="test-key",
            model="gpt-4o-mini",
            timeout_seconds=5,
        )
        monkeypatch.setattr(httpx.AsyncClient, "post", self._mock_post_400_context_overflow)

        # Act & Assert
        with pytest.raises(ProviderLimitExceededError):
            await generator.generate(StudyText(value="The capital of France is Paris."))

    async def test_raises_generation_error_when_400_is_not_context_overflow(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Arrange: an ordinary 400 (e.g. malformed request) must not be
        # misclassified as a provider limit.
        generator = OpenAICompatibleGenerator(
            base_url="http://example.com/v1",
            api_key="test-key",
            model="gpt-4o-mini",
            timeout_seconds=5,
        )
        monkeypatch.setattr(httpx.AsyncClient, "post", self._mock_post_400_other)

        # Act & Assert
        with pytest.raises(GenerationError) as exc_info:
            await generator.generate(StudyText(value="The capital of France is Paris."))
        assert not isinstance(exc_info.value, ProviderLimitExceededError)

    async def test_includes_max_tokens_in_request_payload(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Arrange
        generator = OpenAICompatibleGenerator(
            base_url="http://example.com/v1",
            api_key="test-key",
            model="gpt-4o-mini",
            timeout_seconds=5,
        )
        captured: dict[str, object] = {}
        monkeypatch.setattr(
            httpx.AsyncClient, "post", self._capture_request(captured, self._mock_post_success)
        )

        # Act
        await generator.generate(StudyText(value="The capital of France is Paris."))

        # Assert
        payload = captured["json"]
        assert isinstance(payload, dict)
        assert "max_tokens" in payload
        assert isinstance(payload["max_tokens"], int)
        assert payload["max_tokens"] > 0

    async def test_sends_bearer_authorization_model_and_chat_completions_path(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Arrange
        generator = OpenAICompatibleGenerator(
            base_url="http://example.com/v1",
            api_key="test-key",
            model="gpt-4o-mini",
            timeout_seconds=5,
        )
        captured: dict[str, object] = {}
        monkeypatch.setattr(
            httpx.AsyncClient, "post", self._capture_request(captured, self._mock_post_success)
        )

        # Act
        await generator.generate(StudyText(value="The capital of France is Paris."))

        # Assert
        assert captured["url"] == "http://example.com/v1/chat/completions"
        headers = captured["headers"]
        assert isinstance(headers, dict)
        assert headers["Authorization"] == "Bearer test-key"
        payload = captured["json"]
        assert isinstance(payload, dict)
        assert payload["model"] == "gpt-4o-mini"

    # --- mock helpers ---

    def _capture_request(self, captured: dict[str, object], respond):  # type: ignore[no-untyped-def]
        async def _mock(self_client: object, url: str, **kwargs: object) -> httpx.Response:
            captured["url"] = url
            captured.update(kwargs)
            return await respond(url, **kwargs)

        return _mock

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

    async def _mock_post_400_context_overflow(self, url: str, **kwargs: object) -> httpx.Response:
        return httpx.Response(
            400,
            json={
                "error": {
                    "message": "This model's maximum context length is 4096 tokens.",
                    "code": "context_length_exceeded",
                }
            },
        )

    async def _mock_post_400_other(self, url: str, **kwargs: object) -> httpx.Response:
        return httpx.Response(
            400, json={"error": {"message": "Invalid request body", "code": "invalid_request"}}
        )

    async def _mock_post_500(self, url: str, **kwargs: object) -> httpx.Response:
        return httpx.Response(500, json={"error": {"message": "server error"}})

    async def _mock_post_timeout(self, url: str, **kwargs: object) -> httpx.Response:
        raise httpx.TimeoutException("request timed out")
