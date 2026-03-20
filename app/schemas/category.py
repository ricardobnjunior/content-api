"""Pydantic schemas for Category."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    """Schema for creating a new category."""

    name: str = Field(..., max_length=100)
    description: Optional[str] = None


class CategoryUpdate(BaseModel):
    """Schema for updating an existing category."""

    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = None


class CategoryResponse(BaseModel):
    """Schema for category responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    description: Optional[str] = None
