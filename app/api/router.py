"""Central API router for version 1 endpoints."""

from fastapi import APIRouter

# Future feature routers will be included here via api_router.include_router()
api_router = APIRouter(prefix="/api/v1")
