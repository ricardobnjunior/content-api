"""FastAPI application entry point."""

from fastapi import FastAPI

from app.api.router import api_router
from app.config import get_settings
from app.database import create_tables

settings = get_settings()

app = FastAPI(title="Content API")

create_tables()

app.include_router(api_router)


@app.get("/health")
def health_check() -> dict:
    """Return service health status.

    Returns:
        dict: Health status and current environment name.
    """
    return {"status": "ok", "environment": settings.environment}
