"""Unit tests for application settings validation and defaults."""

import logging

import pytest

from src.config import ConfigurationError, Settings


class TestSettingsValidation:
    def test_raises_when_production_env_uses_stub_provider(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Arrange
        monkeypatch.setenv("APP_ENV", "production")
        monkeypatch.setenv("LLM_PROVIDER", "stub")

        # Act & Assert
        with pytest.raises(ConfigurationError, match="stub"):
            Settings()

    def test_raises_when_llm_provider_is_unrecognized(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Arrange
        monkeypatch.setenv("APP_ENV", "development")
        monkeypatch.setenv("LLM_PROVIDER", "opneai")  # typo

        # Act & Assert
        with pytest.raises(ConfigurationError, match="LLM_PROVIDER"):
            Settings()

    def test_max_input_bytes_defaults_to_ten_mebibytes(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Arrange
        monkeypatch.delenv("MAX_INPUT_BYTES", raising=False)
        monkeypatch.setenv("LLM_PROVIDER", "stub")
        monkeypatch.setenv("APP_ENV", "development")

        # Act
        settings = Settings()

        # Assert
        assert settings.max_input_bytes == 10 * 1024 * 1024

    def test_warns_when_stub_active_outside_production(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        # Arrange
        monkeypatch.setenv("APP_ENV", "development")
        monkeypatch.setenv("LLM_PROVIDER", "stub")

        # Act
        with caplog.at_level(logging.WARNING):
            Settings()

        # Assert
        assert any("stub" in record.message.lower() for record in caplog.records)

    def test_accepts_openai_provider_in_production(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # Arrange
        monkeypatch.setenv("APP_ENV", "production")
        monkeypatch.setenv("LLM_PROVIDER", "openai")

        # Act
        settings = Settings()

        # Assert
        assert settings.llm_provider == "openai"
