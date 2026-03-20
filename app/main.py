"""FastAPI application entry point."""

from fastapi import FastAPI

from app.api.router import api_router
from app.config import get_settings
from app.database import create_tables

settings = get_settings()

app = FastAPI(title="Content API")

# Create database tables on startup
create_tables()

# Register API routes
app.include_router(api_router)


@app.get("/health")
def health_check() -> dict:
    """Return application health status.

    Returns:
        dict: A mapping with status and current environment name.
    """
    return {"status": "ok", "environment": settings.environment}
