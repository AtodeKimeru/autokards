"""OpenAI-compatible LLM flashcard generator infrastructure adapter.

Communicates with any OpenAI-compatible chat-completions endpoint (OpenAI,
OpenRouter, Ollama, LM Studio) via ``httpx``. Configured through environment
variables: ``LLM_BASE_URL``, ``LLM_API_KEY``, ``LLM_MODEL``,
``LLM_TIMEOUT_SECONDS``.

Strict output parsing requires a JSON array of ``{front, back}`` objects;
malformed JSON, zero cards, empty fields, or non-string values raise
:class:`InvalidGeneratorOutputError`. Provider context-limit responses raise
:class:`ProviderLimitExceededError`: HTTP 422, or HTTP 400 whose error
payload signals a context-length overflow (OpenAI, OpenRouter, Ollama, and
LM Studio all report overflow as HTTP 400, so a literal-422-only check would
make this scenario unreachable). All other failures raise
:class:`GenerationError`.
"""

import json
from typing import Any

import httpx

from src.config import settings
from src.domain.exceptions import (
    GenerationError,
    InvalidGeneratorOutputError,
    ProviderLimitExceededError,
)
from src.domain.models.flashcard import Flashcard
from src.domain.models.study_text import StudyText
from src.domain.ports.flashcard_generator import FlashcardGenerator

_DEFAULT_MAX_TOKENS = 2000

_CONTEXT_OVERFLOW_SIGNALS = (
    "context_length_exceeded",
    "context length",
    "maximum context length",
    "context_length",
)

_SYSTEM_PROMPT = """You are a flashcard generator. Given study text, produce flashcards
for spaced repetition. Return ONLY a JSON array of objects, each with exactly
two keys: "front" and "back".

Rules:
1. Each Front must present exactly ONE identifiable retrieval target (one
   question, prompt, or concept). Do not combine multiple independent questions
   in a single Front.
2. Each Back must be a non-empty answer to its Front.
3. Every factual claim in a Back must be supported by the submitted study
   text. Do not introduce unsupported facts.
4. Use the same language as the source text.
5. Output valid JSON only, no markdown fences, no extra prose.
"""


class OpenAICompatibleGenerator(FlashcardGenerator):
    """OpenAI-compatible chat-completions adapter for flashcard generation."""

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        timeout_seconds: int | None = None,
    ) -> None:
        self.base_url = base_url or settings.llm_base_url
        self.api_key = api_key or settings.llm_api_key
        self.model = model or settings.llm_model
        self.timeout_seconds = timeout_seconds or settings.llm_timeout_seconds

    async def generate(self, study_text: StudyText) -> tuple[Flashcard, ...]:
        """Generate flashcards from validated study text via an LLM provider.

        Args:
            study_text: Study text that passed input validation.

        Returns:
            A non-empty tuple of flashcards.

        Raises:
            ProviderLimitExceededError: When the provider rejects the input as
                exceeding its own limit (HTTP 422).
            InvalidGeneratorOutputError: When output is malformed, empty, or
                contains empty/non-string fields.
            GenerationError: On any other provider failure or timeout.
        """
        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": study_text.value},
            ],
            "temperature": 0.3,
            "max_tokens": _DEFAULT_MAX_TOKENS,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(
                    f"{self.base_url.rstrip('/')}/chat/completions",
                    headers=headers,
                    json=payload,
                )
        except httpx.TimeoutException as exc:
            raise GenerationError("Generation request timed out") from exc
        except httpx.RequestError as exc:
            raise GenerationError(f"Generation request failed: {exc}") from exc

        if response.status_code == 422 or self._is_context_overflow(response):
            raise ProviderLimitExceededError("Input exceeds provider limit")

        if response.status_code >= 400:
            raise GenerationError(f"Provider returned HTTP {response.status_code}")

        return self._parse_output(response)

    def _is_context_overflow(self, response: httpx.Response) -> bool:
        """Detect a context-length overflow reported as HTTP 400.

        OpenAI, OpenRouter, Ollama, and LM Studio surface this condition as
        HTTP 400 with an error payload naming the overflow, rather than 422.
        """
        if response.status_code != 400:
            return False
        try:
            body = response.json()
        except (ValueError, json.JSONDecodeError):
            return False
        if not isinstance(body, dict):
            return False
        error = body.get("error")
        error_text = ""
        if isinstance(error, dict):
            error_text = f"{error.get('code', '')} {error.get('message', '')}"
        elif isinstance(error, str):
            error_text = error
        error_text = error_text.lower()
        return any(signal in error_text for signal in _CONTEXT_OVERFLOW_SIGNALS)

    def _parse_output(self, response: httpx.Response) -> tuple[Flashcard, ...]:
        """Parse and strictly validate the provider's JSON output."""
        try:
            body = response.json()
        except (ValueError, json.JSONDecodeError) as exc:
            raise InvalidGeneratorOutputError("Provider response is not valid JSON") from exc

        content = self._extract_content(body)
        cards = self._parse_cards(content)
        return tuple(cards)

    def _extract_content(self, body: dict[str, Any]) -> str:
        choices = body.get("choices")
        if not isinstance(choices, list) or not choices:
            raise InvalidGeneratorOutputError("Provider response has no choices")
        first_choice = choices[0]
        if not isinstance(first_choice, dict):
            raise InvalidGeneratorOutputError("Provider choice is not an object")
        message = first_choice.get("message")
        if not isinstance(message, dict):
            raise InvalidGeneratorOutputError("Provider message is not an object")
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise InvalidGeneratorOutputError("Provider content is empty or missing")
        return content

    def _parse_cards(self, content: str) -> list[Flashcard]:
        try:
            data = json.loads(content)
        except (ValueError, json.JSONDecodeError) as exc:
            raise InvalidGeneratorOutputError("Card content is not valid JSON") from exc

        if not isinstance(data, list):
            raise InvalidGeneratorOutputError("Card content is not a JSON array")
        if not data:
            raise InvalidGeneratorOutputError("Card content is an empty array")

        cards: list[Flashcard] = []
        for index, item in enumerate(data):
            if not isinstance(item, dict):
                raise InvalidGeneratorOutputError(f"Card at index {index} is not an object")
            front = item.get("front")
            back = item.get("back")
            if not isinstance(front, str) or not front.strip():
                raise InvalidGeneratorOutputError(
                    f"Card at index {index} has an empty or non-string Front"
                )
            if not isinstance(back, str) or not back.strip():
                raise InvalidGeneratorOutputError(
                    f"Card at index {index} has an empty or non-string Back"
                )
            cards.append(Flashcard(front=front.strip(), back=back.strip()))

        return cards
