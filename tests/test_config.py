"""Tests for app/config.py — Settings and get_settings()."""

import os
from functools import lru_cache
from unittest.mock import patch

import pytest


def test_settings_default_database_url():
    """Settings should have a default database_url."""
    from app.config import Settings

    s = Settings()
    assert s.database_url == "sqlite:///content.db"


def test_settings_default_secret_key():
    """Settings should have a default secret_key."""
    from app.config import Settings

    s = Settings()
    assert s.secret_key == "dev-secret-change-in-production"


def test_settings_default_environment():
    """Settings should default to 'development'."""
    from app.config import Settings

    s = Settings()
    assert s.environment == "development"


def test_settings_override_via_env():
    """Settings should pick up overrides from environment variables."""
    from app.config import Settings

    with patch.dict(
        os.environ,
        {
            "DATABASE_URL": "sqlite:///custom.db",
            "SECRET_KEY": "my-secret",
            "ENVIRONMENT": "production",
        },
    ):
        s = Settings()
        assert s.database_url == "sqlite:///custom.db"
        assert s.secret_key == "my-secret"
        assert s.environment == "production"


def test_get_settings_returns_settings_instance():
    """get_settings() should return a Settings instance."""
    from app.config import Settings, get_settings  # noqa: E402

    result = get_settings()
    assert isinstance(result, Settings)


def test_get_settings_is_cached():
    """get_settings() should return the same object on repeated calls (lru_cache)."""
    from app.config import get_settings  # noqa: E402

    first = get_settings()
    second = get_settings()
    assert first is second


def test_settings_lowercase_field_access():
    """Settings fields must be accessible via lowercase names."""
    from app.config import Settings  # noqa: E402

    s = Settings()
    # These attribute accesses must not raise AttributeError
    _ = s.database_url
    _ = s.secret_key
    _ = s.environment
