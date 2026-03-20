import os
from unittest.mock import patch


def test_settings_defaults():
    from importlib import reload
    import app.config as config_module  # noqa: E402
    from app.config import Settings  # noqa: E402

    reload(config_module)
    settings = Settings()
    assert settings.database_url is not None
    assert isinstance(settings.database_url, str)


def test_settings_from_env():
    from app.config import Settings  # noqa: E402

    with patch.dict(os.environ, {"DATABASE_URL": "sqlite:///test.db"}):
        settings = Settings()
        assert settings.database_url == "sqlite:///test.db"


def test_settings_openrouter_api_key_empty_by_default():
    from app.config import Settings  # noqa: E402

    settings = Settings()
    assert settings.openrouter_api_key == "" or settings.openrouter_api_key is None


def test_settings_openrouter_model_has_default():
    from app.config import Settings  # noqa: E402

    settings = Settings()
    assert settings.openrouter_model is not None
    assert isinstance(settings.openrouter_model, str)
    assert len(settings.openrouter_model) > 0


def test_get_settings_returns_settings_instance():
    from app.config import Settings, get_settings  # noqa: E402

    settings = get_settings()
    assert isinstance(settings, Settings)
