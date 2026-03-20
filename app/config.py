"""Application configuration using Pydantic Settings."""

import json
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Attributes:
        database_url: SQLAlchemy database connection string.
        secret_key: Secret key for JWT token signing.
        upload_dir: Directory for uploaded files.
        openrouter_api_key: API key for OpenRouter LLM service.
        openrouter_model: Model identifier to use with OpenRouter.
    """

    database_url: str
    secret_key: str
    upload_dir: str = "uploads"
    openrouter_api_key: str = ""
    openrouter_model: str = "google/gemini-2.5-flash"

    model_config = {"env_file": ".env", "case_sensitive": False}


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings.

    Returns:
        Settings: The application settings instance.
    """
    return Settings()


settings = get_settings()
