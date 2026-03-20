"""Main API router that aggregates all endpoint routers."""

from fastapi import APIRouter

from app.api.endpoints.articles import router as articles_router
from app.api.endpoints.categories import router as categories_router
from app.api.endpoints.suggestions import router as suggestions_router

router = APIRouter(prefix="/api/v1")

router.include_router(articles_router)
router.include_router(categories_router)
router.include_router(suggestions_router)
