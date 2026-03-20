"""Main API router aggregating all endpoint sub-routers."""

from fastapi import APIRouter

from app.api.endpoints.suggestions import router as suggestions_router

main_router = APIRouter(prefix="/api/v1")

main_router.include_router(articles_router)
main_router.include_router(categories_router)
main_router.include_router(suggestions_router)
