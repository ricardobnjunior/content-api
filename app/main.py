"""Main FastAPI application."""

from fastapi import FastAPI

from app.api.router import router as api_router

app = FastAPI(title="Article API")

app.include_router(api_router, prefix="/api/v1")
