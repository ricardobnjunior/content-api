"""Central API router with versioned prefix."""

from fastapi import APIRouter

api_router = APIRouter(prefix="/api/v1")
