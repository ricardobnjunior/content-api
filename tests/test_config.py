"""Tests for application configuration (app/config.py)."""

import os
from unittest.mock import patch


def test_settings_default_database_url():
    """Settings should have a default database_url."""
    from app.config import Settings

    with patch.dict(os.environ, {}, clear=False):
        # Remove potentially set env vars to test defaults
        env = {k: v for k, v in os.environ.items() 
               if k.upper() not in ("DATABASE_URL", "SECRET_KEY", "ENVIRONMENT")}
        with patch.dict(os.environ, env, clear=True):
            s = Settings()
            assert s.database_url == "sqlite:///content.db"


def test_settings_default_secret_key():
    """Settings should have a default secret_key."""
    from app.config import Settings  # noqa: E402

    env = {k: v for k, v in os.environ.items() 
           if k.upper() not in ("DATABASE_URL", "SECRET_KEY", "ENVIRONMENT")}
    with patch.dict(os.environ, env, clear=True):
        s = Settings()
        assert s.secret_key == "dev-secret-change-in-production"


def test_settings_default_environment():
    """Settings should default environment to 'development'."""
    from app.config import Settings  # noqa: E402

    env = {k: v for k, v in os.environ.items() 
           if k.upper() not in ("DATABASE_URL", "SECRET_KEY", "ENVIRONMENT")}
    with patch.dict(os.environ, env, clear=True):
        s = Settings()
        assert s.environment == "development"


def test_settings_override_via_env():
    """Settings fields can be overridden via environment variables."""
    from app.config import Settings  # noqa: E402

    with patch.dict(os.environ, {"DATABASE_URL": "sqlite:///custom.db", "ENVIRONMENT": "production"}):
        s = Settings()
        assert s.database_url == "sqlite:///custom.db"
        assert s.environment == "production"


def test_settings_field_names_are_lowercase():
    """Settings instance uses lowercase attribute names."""
    from app.config import Settings  # noqa: E402

    s = Settings()
    assert hasattr(s, "database_url")
    assert hasattr(s, "secret_key")
    assert hasattr(s, "environment")


def test_get_settings_returns_settings_instance():
    """get_settings() returns a Settings object."""
    from app.config import Settings, get_settings  # noqa: E402

    result = get_settings()
    assert isinstance(result, Settings)


def test_get_settings_is_cached():
    """get_settings() returns the same instance on repeated calls (lru_cache)."""
    from app.config import get_settings  # noqa: E402

    first = get_settings()
    second = get_settings()
    assert first is second
