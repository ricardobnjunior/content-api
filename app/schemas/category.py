"""Pydantic schemas for Category endpoints."""

from pydantic import BaseModel


class CategoryCreate(BaseModel):
    """Schema for creating a new category."""
    name: str


class CategoryResponse(BaseModel):
    """Schema returned by category endpoints."""
    id: int
    name: str

    model_config = {"from_attributes": True}
