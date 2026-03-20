"""Application configuration using Pydantic Settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Attributes:
        database_url: SQLAlchemy database connection URL.
        secret_key: Secret key for JWT token signing.
        upload_dir: Directory for uploaded files.
        openrouter_api_key: API key for OpenRouter LLM service.
        openrouter_model: Model identifier to use via OpenRouter.
    """

    database_url: str = "sqlite:///./app.db"
    secret_key: str = "changeme"
    upload_dir: str = "uploads"
    openrouter_api_key: str = ""
    openrouter_model: str = "google/gemini-2.5-flash"

    model_config = {"env_file": ".env", "case_sensitive": False}


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings instance.

    Returns:
        Settings: The application settings object.
    """
    return Settings()


settings = get_settings()
