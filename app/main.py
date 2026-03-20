"""FastAPI application entry point."""

from fastapi import FastAPI

from app.api.router import api_router
from app.database import create_tables

app = FastAPI(title="Article API")

# Create tables on startup
create_tables()

app.include_router(api_router)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
