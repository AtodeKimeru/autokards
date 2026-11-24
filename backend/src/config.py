"""Application configuration loaded from environment variables."""

import logging
import os

logger = logging.getLogger(__name__)

_VALID_LLM_PROVIDERS = {"stub", "openai"}
_DEFAULT_MAX_INPUT_BYTES = 10 * 1024 * 1024  # 10 MiB, aligned with FR-1


class ConfigurationError(Exception):
    """Raised when runtime configuration is invalid and the app must not start."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


def _get_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).lower() in {"1", "true", "yes", "on"}


def _get_int(name: str, default: int) -> int:
    return int(os.getenv(name, str(default)))


class Settings:
    """Runtime configuration.

    Values are loaded from environment variables with sensible defaults
    for local development. Secrets should never be hardcoded.

    Raises:
        ConfigurationError: When ``LLM_PROVIDER`` is unrecognized, or when
            ``APP_ENV=production`` is combined with ``LLM_PROVIDER=stub``.
            The stub returns input-agnostic cards, so serving it in
            production would fabricate ungrounded material; an unrecognized
            provider must not silently fall through to the real adapter.
    """

    def __init__(self) -> None:
        self.app_name = os.getenv("APP_NAME", "autokards-backend")
        self.debug = _get_bool("DEBUG", False)
        self.app_env = os.getenv("APP_ENV", "development")

        # LLM provider configuration (FR-4)
        self.llm_provider = os.getenv("LLM_PROVIDER", "stub")
        self.llm_base_url = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
        self.llm_api_key = os.getenv("LLM_API_KEY", "")
        self.llm_model = os.getenv("LLM_MODEL", "gpt-4o-mini")
        self.llm_timeout_seconds = _get_int("LLM_TIMEOUT_SECONDS", 30)

        # Input byte ceiling (FR-4, aligned with FR-1's AUTOKARDS_MAX_INPUT_BYTES)
        self.max_input_bytes = _get_int("MAX_INPUT_BYTES", _DEFAULT_MAX_INPUT_BYTES)

        self._validate_llm_provider()

    def _validate_llm_provider(self) -> None:
        if self.llm_provider not in _VALID_LLM_PROVIDERS:
            raise ConfigurationError(
                f"LLM_PROVIDER={self.llm_provider!r} is not recognized; "
                f"expected one of {sorted(_VALID_LLM_PROVIDERS)}"
            )
        if self.app_env == "production" and self.llm_provider == "stub":
            raise ConfigurationError(
                "LLM_PROVIDER=stub is not allowed when APP_ENV=production; "
                "configure a real provider or unset APP_ENV"
            )
        if self.llm_provider == "stub" and self.app_env != "production":
            logger.warning(
                "LLM_PROVIDER=stub is active outside production (APP_ENV=%s); "
                "generated flashcards are fabricated and not grounded in input.",
                self.app_env,
            )


settings = Settings()
