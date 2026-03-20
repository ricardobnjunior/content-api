"""Central API router with /api/v1 prefix.

Future feature routers should be included here via include_router().
"""

from fastapi import APIRouter

api_router = APIRouter(prefix="/api/v1")

# Future routers will be registered here, e.g.:
# from app.api.endpoints import items
# api_router.include_router(items.router, prefix="/items", tags=["items"])
