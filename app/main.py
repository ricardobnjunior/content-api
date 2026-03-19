"""FastAPI application entry point."""

from fastapi import FastAPI

from app.api.router import api_router
from app.database import create_tables

app = FastAPI(title="Articles API")

app.include_router(api_router)


@app.on_event("startup")
def startup_event():
    create_tables()


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
