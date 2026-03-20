"""Image upload schemas."""

from pydantic import BaseModel


class ImageResponse(BaseModel):
    """Response schema for image upload.

    Attributes:
        filename: The stored filename of the uploaded image.
        url: The URL path to access the uploaded image.
        size: File size in bytes.
    """

    filename: str
    url: str
    size: int
