"""Category Pydantic schemas."""

from pydantic import BaseModel


class CategoryCreate(BaseModel):
    """Schema for creating a category.

    Attributes:
        name: Category name.
    """

    name: str


class CategoryResponse(BaseModel):
    """Schema for category API responses.

    Attributes:
        id: Category primary key.
        name: Category name.
    """

    id: int
    name: str

    model_config = {"from_attributes": True}
