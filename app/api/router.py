"""Central API router."""

from fastapi import APIRouter


api_router = APIRouter(prefix="/api/v1")
api_router.include_router(articles.router, prefix="/articles", tags=["articles"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
