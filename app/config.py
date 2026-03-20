"""Application configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./app.db"
    secret_key: str = "default-secret-key"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
