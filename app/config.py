"""Application configuration using pydantic-settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""

    model_config = SettingsConfigDict(
        env_file=None,
        env_ignore_empty=False,
        case_sensitive=False,
        extra="ignore",
    )

    database_url: str = "sqlite:///content.db"
    secret_key: str = "dev-secret-change-in-production"
    environment: str = "development"


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings instance."""
    return Settings()


settings = get_settings()
