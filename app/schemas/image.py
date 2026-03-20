"""Pydantic schemas for image upload responses."""

from pydantic import BaseModel


class ImageResponse(BaseModel):
    """Schema for image upload response.

    Attributes:
        filename: Name of the uploaded file.
        url: Public URL path to access the image.
        size: File size in bytes.
    """

    filename: str
    url: str
    size: int
