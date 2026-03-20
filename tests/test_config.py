"""Tests for application configuration."""

import pytest

from app.config import Settings, get_settings


def test_default_upload_dir() -> None:
    """Test that the default upload_dir is 'uploads'."""
    settings = Settings()
    assert settings.upload_dir == "uploads"


def test_default_environment() -> None:
    """Test that the default environment is 'development'."""
    settings = Settings()
    assert settings.environment == "development"


def test_default_database_url_contains_sqlite() -> None:
    """Test that the default database_url uses sqlite."""
    settings = Settings()
    assert "sqlite" in settings.database_url


def test_upload_dir_can_be_overridden() -> None:
    """Test that upload_dir can be set to a custom value."""
    settings = Settings()
    settings.upload_dir = "/tmp/custom_uploads"
    assert settings.upload_dir == "/tmp/custom_uploads"


def test_get_settings_returns_singleton() -> None:
    """Test that get_settings returns a cached singleton."""
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2


def test_settings_has_secret_key() -> None:
    """Test that Settings has a non-empty secret_key field."""
    settings = Settings()
    assert settings.secret_key
    assert isinstance(settings.secret_key, str)
