"""Main FastAPI application."""

from fastapi import FastAPI

from app.api.router import router
from app.database import Base, engine

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Article API")

app.include_router(router, prefix="/api")
