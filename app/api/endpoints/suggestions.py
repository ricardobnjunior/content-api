"""Suggestions endpoint."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def list_suggestions():
    """List suggestions."""
    return []
