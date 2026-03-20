"""Application configuration settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    database_url: str = "sqlite:///./test.db"
    secret_key: str = "test-secret-key"
    upload_dir: str = "uploads"
    openrouter_api_key: str = "test-api-key"
    openrouter_model: str = "openai/gpt-4o-mini"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
