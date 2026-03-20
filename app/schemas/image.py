"""Pydantic schemas for image uploads."""

from pydantic import BaseModel


class ImageResponse(BaseModel):
    """Schema for image upload API responses.

    Attributes:
        filename: Name of the saved file on disk.
        url: Public URL to access the uploaded image.
        size: File size in bytes.
    """

    filename: str
    url: str
    size: int
