"""Tests for the ImageResponse schema."""

import pytest

from app.schemas.image import ImageResponse


def test_image_response_valid() -> None:
    """Test creating a valid ImageResponse instance."""
    response = ImageResponse(
        filename="1_photo.jpg",
        url="/uploads/1_photo.jpg",
        size=1024,
    )
    assert response.filename == "1_photo.jpg"
    assert response.url == "/uploads/1_photo.jpg"
    assert response.size == 1024


def test_image_response_zero_size() -> None:
    """Test ImageResponse with zero byte size (edge case)."""
    response = ImageResponse(
        filename="empty.jpg",
        url="/uploads/empty.jpg",
        size=0,
    )
    assert response.size == 0


def test_image_response_missing_filename() -> None:
    """Test that ImageResponse raises validation error when filename is missing."""
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        ImageResponse(url="/uploads/photo.jpg", size=512)  # type: ignore[call-arg]


def test_image_response_missing_url() -> None:
    """Test that ImageResponse raises validation error when url is missing."""
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        ImageResponse(filename="photo.jpg", size=512)  # type: ignore[call-arg]


def test_image_response_missing_size() -> None:
    """Test that ImageResponse raises validation error when size is missing."""
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        ImageResponse(filename="photo.jpg", url="/uploads/photo.jpg")  # type: ignore[call-arg]


def test_image_response_serialization() -> None:
    """Test that ImageResponse serializes to dict correctly."""
    response = ImageResponse(
        filename="42_banner.png",
        url="/uploads/42_banner.png",
        size=2048,
    )
    data = response.model_dump()
    assert data == {
        "filename": "42_banner.png",
        "url": "/uploads/42_banner.png",
        "size": 2048,
    }


def test_image_response_large_size() -> None:
    """Test ImageResponse with a large file size value."""
    response = ImageResponse(
        filename="large_image.jpg",
        url="/uploads/large_image.jpg",
        size=10 * 1024 * 1024,  # 10 MB
    )
    assert response.size == 10 * 1024 * 1024
