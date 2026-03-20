"""Tests for the article image upload and delete endpoints."""

import io
import os

import pytest
from fastapi.testclient import TestClient


def _create_article(client: TestClient) -> dict:
    """Helper: create a test article via the API and return its JSON.

    Args:
        client: Test client instance.

    Returns:
        Parsed JSON response body for the created article.
    """
    response = client.post(
        "/api/articles/",
        json={"title": "Test Article", "content": "Test content", "status": "draft"},
    )
    assert response.status_code == 201, response.text
    return response.json()


def _make_image_file(
    filename: str = "photo.jpg",
    content: bytes = b"fake-jpeg-content",
    content_type: str = "image/jpeg",
) -> tuple:
    """Build a file tuple suitable for multipart upload.

    Args:
        filename: Original filename of the upload.
        content: Raw byte content of the file.
        content_type: MIME type of the file.

    Returns:
        Tuple of (field_name, (filename, file_object, content_type)).
    """
    return ("file", (filename, io.BytesIO(content), content_type))


class TestUploadImage:
    """Tests for POST /api/articles/{article_id}/image."""

    def test_upload_valid_image_returns_201(self, client: TestClient) -> None:
        """Uploading a valid image returns 201 and correct ImageResponse fields."""
        article = _create_article(client)
        article_id = article["id"]

        response = client.post(
            f"/api/articles/{article_id}/image",
            files=[_make_image_file()],
        )

        assert response.status_code == 201, response.text
        body = response.json()
        assert "filename" in body
        assert "url" in body
        assert "size" in body
        assert body["url"].startswith("/uploads/")
        assert str(article_id) in body["filename"]
        assert body["size"] > 0

    def test_upload_valid_image_saves_file_to_disk(
        self, client: TestClient, override_upload_dir: str
    ) -> None:
        """Uploading a valid image saves the file to the upload directory."""
        article = _create_article(client)
        article_id = article["id"]
        file_content = b"binary-image-data-here"

        response = client.post(
            f"/api/articles/{article_id}/image",
            files=[_make_image_file(content=file_content)],
        )

        assert response.status_code == 201, response.text
        saved_filename = response.json()["filename"]
        file_path = os.path.join(override_upload_dir, saved_filename)
        assert os.path.exists(file_path), f"Expected file at {file_path}"
        with open(file_path, "rb") as f:
            assert f.read() == file_content

    def test_upload_updates_article_image_url(self, client: TestClient) -> None:
        """After upload, GET /articles/{id} returns the updated image_url."""
        article = _create_article(client)
        article_id = article["id"]

        upload_response = client.post(
            f"/api/articles/{article_id}/image",
            files=[_make_image_file()],
        )
        assert upload_response.status_code == 201, upload_response.text
        expected_url = upload_response.json()["url"]

        get_response = client.get(f"/api/articles/{article_id}")
        assert get_response.status_code == 200, get_response.text
        assert get_response.json()["image_url"] == expected_url

    def test_upload_nonexistent_article_returns_404(self, client: TestClient) -> None:
        """Uploading an image for a non-existent article returns 404."""
        response = client.post(
            "/api/articles/99999/image",
            files=[_make_image_file()],
        )
        assert response.status_code == 404, response.text

    def test_upload_non_image_file_returns_400(self, client: TestClient) -> None:
        """Uploading a non-image file returns 400."""
        article = _create_article(client)
        article_id = article["id"]

        response = client.post(
            f"/api/articles/{article_id}/image",
            files=[_make_image_file(
                filename="document.txt",
                content=b"plain text content",
                content_type="text/plain",
            )],
        )
        assert response.status_code == 400, response.text

    def test_upload_non_image_application_octet_returns_400(
        self, client: TestClient
    ) -> None:
        """Uploading a file with application/octet-stream content type returns 400."""
        article = _create_article(client)
        article_id = article["id"]

        response = client.post(
            f"/api/articles/{article_id}/image",
            files=[_make_image_file(
                filename="binary.bin",
                content=b"\x00\x01\x02\x03",
                content_type="application/octet-stream",
            )],
        )
        assert response.status_code == 400, response.text

    def test_upload_png_image_is_accepted(self, client: TestClient) -> None:
        """Uploading a PNG image is accepted (status 201)."""
        article = _create_article(client)
        article_id = article["id"]

        response = client.post(
            f"/api/articles/{article_id}/image",
            files=[_make_image_file(
                filename="icon.png",
                content=b"\x89PNG\r\n\x1a\n",
                content_type="image/png",
            )],
        )
        assert response.status_code == 201, response.text


class TestDeleteImage:
    """Tests for DELETE /api/articles/{article_id}/image."""

    def test_delete_image_returns_204(self, client: TestClient) -> None:
        """Deleting an article image returns 204."""
        article = _create_article(client)
        article_id = article["id"]

        # Upload first
        client.post(
            f"/api/articles/{article_id}/image",
            files=[_make_image_file()],
        )

        response = client.delete(f"/api/articles/{article_id}/image")
        assert response.status_code == 204, response.text

    def test_delete_image_removes_file_from_disk(
        self, client: TestClient, override_upload_dir: str
    ) -> None:
        """After delete, the image file is removed from disk."""
        article = _create_article(client)
        article_id = article["id"]

        upload_response = client.post(
            f"/api/articles/{article_id}/image",
            files=[_make_image_file()],
        )
        saved_filename = upload_response.json()["filename"]
        file_path = os.path.join(override_upload_dir, saved_filename)
        assert os.path.exists(file_path)

        client.delete(f"/api/articles/{article_id}/image")
        assert not os.path.exists(file_path), "File should have been deleted"

    def test_delete_image_clears_image_url(self, client: TestClient) -> None:
        """After delete, GET /articles/{id} returns image_url=None."""
        article = _create_article(client)
        article_id = article["id"]

        client.post(
            f"/api/articles/{article_id}/image",
            files=[_make_image_file()],
        )

        client.delete(f"/api/articles/{article_id}/image")

        get_response = client.get(f"/api/articles/{article_id}")
        assert get_response.status_code == 200, get_response.text
        assert get_response.json()["image_url"] is None

    def test_delete_nonexistent_article_returns_404(self, client: TestClient) -> None:
        """Deleting an image for a non-existent article returns 404."""
        response = client.delete("/api/articles/99999/image")
        assert response.status_code == 404, response.text

    def test_delete_image_when_no_file_on_disk_returns_204(
        self, client: TestClient, override_upload_dir: str
    ) -> None:
        """Delete succeeds (204) even if the file is already missing from disk."""
        article = _create_article(client)
        article_id = article["id"]

        upload_response = client.post(
            f"/api/articles/{article_id}/image",
            files=[_make_image_file()],
        )
        saved_filename = upload_response.json()["filename"]
        file_path = os.path.join(override_upload_dir, saved_filename)

        # Manually remove the file before calling the delete endpoint
        if os.path.exists(file_path):
            os.remove(file_path)

        response = client.delete(f"/api/articles/{article_id}/image")
        assert response.status_code == 204, response.text

    def test_delete_image_no_image_on_article_returns_204(
        self, client: TestClient
    ) -> None:
        """Deleting when article has no image_url returns 204 without error."""
        article = _create_article(client)
        article_id = article["id"]
        assert article["image_url"] is None

        response = client.delete(f"/api/articles/{article_id}/image")
        assert response.status_code == 204, response.text


class TestArticleResponseIncludesImageUrl:
    """Tests ensuring image_url appears in article responses."""

    def test_new_article_has_null_image_url(self, client: TestClient) -> None:
        """A newly created article has image_url=None."""
        article = _create_article(client)
        assert article["image_url"] is None

    def test_image_url_in_list_response(self, client: TestClient) -> None:
        """image_url is present in the paginated article list response."""
        article = _create_article(client)
        article_id = article["id"]

        client.post(
            f"/api/articles/{article_id}/image",
            files=[_make_image_file()],
        )

        list_response = client.get("/api/articles/")
        assert list_response.status_code == 200, list_response.text
        items = list_response.json()["items"]
        matching = [a for a in items if a["id"] == article_id]
        assert matching, "Article not found in list response"
        assert matching[0]["image_url"] is not None
        assert matching[0]["image_url"].startswith("/uploads/")

    def test_upload_replaces_existing_image_url(self, client: TestClient) -> None:
        """Uploading a second image replaces the article's image_url."""
        article = _create_article(client)
        article_id = article["id"]

        first_response = client.post(
            f"/api/articles/{article_id}/image",
            files=[_make_image_file(filename="first.jpg")],
        )
        first_url = first_response.json()["url"]

        second_response = client.post(
            f"/api/articles/{article_id}/image",
            files=[_make_image_file(filename="second.jpg")],
        )
        second_url = second_response.json()["url"]

        assert first_url != second_url

        get_response = client.get(f"/api/articles/{article_id}")
        assert get_response.json()["image_url"] == second_url
