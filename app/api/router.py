"""Central API router with version prefix."""

from fastapi import APIRouter

api_router = APIRouter(prefix="/api/v1")

# Future endpoint routers will be added here via api_router.include_router()
