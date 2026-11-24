"""Application configuration loaded from environment variables."""

import os


def _get_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).lower() in {"1", "true", "yes", "on"}


def _get_int(name: str, default: int) -> int:
    return int(os.getenv(name, str(default)))


class Settings:
    """Runtime configuration.

    Values are loaded from environment variables with sensible defaults
    for local development. Secrets should never be hardcoded.
    """

    def __init__(self) -> None:
        self.app_name = os.getenv("APP_NAME", "autokards-backend")
        self.debug = _get_bool("DEBUG", False)

        # LLM provider configuration (FR-4)
        self.llm_provider = os.getenv("LLM_PROVIDER", "stub")
        self.llm_base_url = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
        self.llm_api_key = os.getenv("LLM_API_KEY", "")
        self.llm_model = os.getenv("LLM_MODEL", "gpt-4o-mini")
        self.llm_timeout_seconds = _get_int("LLM_TIMEOUT_SECONDS", 30)

        # Input byte ceiling (FR-4, shared with companion AUTK-6 reconciliation)
        self.max_input_bytes = _get_int("MAX_INPUT_BYTES", 2000)


settings = Settings()
