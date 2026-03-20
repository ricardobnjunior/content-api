"""Application configuration using pydantic-settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file.

    Attributes:
        database_url: SQLAlchemy database connection URL.
        secret_key: Secret key used for security operations.
        environment: Deployment environment name (e.g., development, production).
    """

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    database_url: str = "sqlite:///content.db"
    secret_key: str = "dev-secret-change-in-production"
    environment: str = "development"


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings instance.

    Returns:
        Singleton Settings instance loaded from environment.
    """
    return Settings()
