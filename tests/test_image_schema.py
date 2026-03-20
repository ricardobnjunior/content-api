"""Tests for ImageResponse schema and article schema image_url field."""

import pytest

from app.schemas.image import ImageResponse
from app.schemas.article import ArticleResponse, ArticleUpdate
from datetime import datetime


class TestImageResponseSchema:
    """Tests for ImageResponse Pydantic schema."""

    def test_image_response_valid(self) -> None:
        """ImageResponse should accept valid filename, url, and size."""
        img = ImageResponse(filename="1_photo.png", url="/uploads/1_photo.png", size=1024)
        assert img.filename == "1_photo.png"
        assert img.url == "/uploads/1_photo.png"
        assert img.size == 1024

    def test_image_response_zero_size(self) -> None:
        """ImageResponse should accept size of zero."""
        img = ImageResponse(filename="empty.png", url="/uploads/empty.png", size=0)
        assert img.size == 0

    def test_image_response_missing_filename_raises(self) -> None:
        """ImageResponse should raise ValidationError when filename is missing."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            ImageResponse(url="/uploads/x.png", size=100)

    def test_image_response_missing_url_raises(self) -> None:
        """ImageResponse should raise ValidationError when url is missing."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            ImageResponse(filename="x.png", size=100)

    def test_image_response_missing_size_raises(self) -> None:
        """ImageResponse should raise ValidationError when size is missing."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            ImageResponse(filename="x.png", url="/uploads/x.png")

    def test_image_response_serialization(self) -> None:
        """ImageResponse.model_dump() should return correct dict."""
        img = ImageResponse(filename="2_test.jpg", url="/uploads/2_test.jpg", size=2048)
        dumped = img.model_dump()
        assert dumped == {"filename": "2_test.jpg", "url": "/uploads/2_test.jpg", "size": 2048}


class TestArticleResponseImageUrl:
    """Tests for image_url field in ArticleResponse."""

    def _make_article_response(self, image_url=None) -> ArticleResponse:
        """Build a minimal ArticleResponse for testing."""
        return ArticleResponse(
            id=1,
            title="Test",
            content="Content",
            status="draft",
            image_url=image_url,
            created_at=datetime(2024, 1, 1, 12, 0, 0),
            updated_at=datetime(2024, 1, 1, 12, 0, 0),
            categories=[],
        )

    def test_image_url_defaults_to_none(self) -> None:
        """ArticleResponse image_url defaults to None."""
        article = self._make_article_response()
        assert article.image_url is None

    def test_image_url_can_be_set(self) -> None:
        """ArticleResponse accepts a non-null image_url."""
        article = self._make_article_response(image_url="/uploads/1_photo.png")
        assert article.image_url == "/uploads/1_photo.png"

    def test_article_response_serializes_image_url(self) -> None:
        """Serialized ArticleResponse includes image_url field."""
        article = self._make_article_response(image_url="/uploads/1_photo.png")
        dumped = article.model_dump()
        assert "image_url" in dumped
        assert dumped["image_url"] == "/uploads/1_photo.png"

    def test_article_response_serializes_null_image_url(self) -> None:
        """Serialized ArticleResponse includes image_url=None when not set."""
        article = self._make_article_response()
        dumped = article.model_dump()
        assert "image_url" in dumped
        assert dumped["image_url"] is None


class TestArticleUpdateImageUrl:
    """Tests for image_url field in ArticleUpdate."""

    def test_article_update_image_url_optional(self) -> None:
        """ArticleUpdate image_url is optional and defaults to None."""
        update = ArticleUpdate()
        assert update.image_url is None

    def test_article_update_image_url_can_be_set(self) -> None:
        """ArticleUpdate accepts image_url value."""
        update = ArticleUpdate(image_url="/uploads/5_pic.jpg")
        assert update.image_url == "/uploads/5_pic.jpg"

    def test_article_update_image_url_in_exclude_unset(self) -> None:
        """When image_url not provided, it should not appear in exclude_unset dump."""
        update = ArticleUpdate(title="New Title")
        dumped = update.model_dump(exclude_unset=True)
        assert "image_url" not in dumped

    def test_article_update_image_url_in_dump_when_set(self) -> None:
        """When image_url provided, it appears in exclude_unset dump."""
        update = ArticleUpdate(image_url="/uploads/1_img.png")
        dumped = update.model_dump(exclude_unset=True)
        assert "image_url" in dumped
        assert dumped["image_url"] == "/uploads/1_img.png"
