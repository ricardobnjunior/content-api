"""Tests for the application configuration settings."""

import os
from unittest.mock import patch


def test_settings_default_values():
    """Default settings are correctly defined."""
    # Clear cache to get fresh instance
    from app.config import get_settings
    get_settings.cache_clear()

    with patch.dict(os.environ, {}, clear=False):
        from app.config import Settings  # noqa: E402
        s = Settings()
        assert s.database_url == "sqlite:///./app.db"
        assert s.upload_dir == "uploads"
        assert s.openrouter_model == "google/gemini-2.5-flash"
        assert s.openrouter_api_key == ""


def test_settings_openrouter_api_key_from_env():
    """openrouter_api_key is loaded from OPENROUTER_API_KEY env var."""
    from app.config import Settings  # noqa: E402

    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "my-secret-key"}):
        s = Settings()
        assert s.openrouter_api_key == "my-secret-key"


def test_settings_openrouter_model_from_env():
    """openrouter_model is loaded from OPENROUTER_MODEL env var."""
    from app.config import Settings  # noqa: E402

    with patch.dict(os.environ, {"OPENROUTER_MODEL": "anthropic/claude-3"}):
        s = Settings()
        assert s.openrouter_model == "anthropic/claude-3"


def test_settings_database_url_from_env():
    """database_url is loaded from DATABASE_URL env var."""
    from app.config import Settings  # noqa: E402

    with patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@localhost/db"}):
        s = Settings()
        assert s.database_url == "postgresql://user:pass@localhost/db"


def test_settings_has_all_required_fields():
    """Settings class has all required fields."""
    from app.config import Settings  # noqa: E402

    s = Settings()
    assert hasattr(s, "database_url")
    assert hasattr(s, "secret_key")
    assert hasattr(s, "upload_dir")
    assert hasattr(s, "openrouter_api_key")
    assert hasattr(s, "openrouter_model")


def test_get_settings_returns_settings_instance():
    """get_settings() returns a Settings instance."""
    from app.config import get_settings, Settings  # noqa: E402

    get_settings.cache_clear()
    s = get_settings()
    assert isinstance(s, Settings)


def test_get_settings_is_cached():
    """get_settings() returns the same instance on repeated calls."""
    from app.config import get_settings  # noqa: E402

    get_settings.cache_clear()
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2
