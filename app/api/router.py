"""Central API router aggregating all endpoint routers."""

from fastapi import APIRouter

from app.api.endpoints.articles import router as articles_router
from app.api.endpoints.categories import router as categories_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(articles_router)
api_router.include_router(categories_router)
