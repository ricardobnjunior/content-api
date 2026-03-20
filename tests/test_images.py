"""Tests for article image upload and delete endpoints."""

import io
import os

import pytest
from fastapi.testclient import TestClient

from app.config import get_settings


def create_test_article(client: TestClient) -> dict:
    """Helper to create a test article via the API.

    Args:
        client: FastAPI TestClient.

    Returns:
        Article response dict.
    """
    payload = {
        "title": "Image Test Article",
        "content": "Content for image test",
        "status": "draft",
    }
    response = client.post("/api/v1/articles", json=payload)
    assert response.status_code == 201, f"Failed to create article: {response.text}"
    return response.json()


def make_image_file(
    filename: str = "test.png",
    content: bytes = b"fake-png-content",
    content_type: str = "image/png",
) -> tuple:
    """Create an in-memory image file tuple for multipart upload.

    Args:
        filename: Name of the file.
        content: File content bytes.
        content_type: MIME type for the file.

    Returns:
        Tuple of (filename, file_object, content_type) for requests.
    """
    return (filename, io.BytesIO(content), content_type)


class TestImageUpload:
    """Tests for POST /{article_id}/image endpoint."""

    def test_upload_valid_image_returns_201(self, client: TestClient) -> None:
        """Upload a valid image file and expect 201 with ImageResponse fields."""
        article = create_test_article(client)
        article_id = article["id"]

        files = {"file": make_image_file()}
        response = client.post(f"/api/v1/articles/{article_id}/image", files=files)

        assert response.status_code == 201
        data = response.json()
        assert "filename" in data
        assert "url" in data
        assert "size" in data
        assert data["url"].startswith("/uploads/")
        assert str(article_id) in data["filename"]
        assert data["size"] > 0

    def test_upload_image_file_saved_to_disk(self, client: TestClient) -> None:
        """Verify the uploaded image file exists on disk after upload."""
        article = create_test_article(client)
        article_id = article["id"]

        file_content = b"fake-image-bytes-for-disk-check"
        files = {"file": ("disk_test.png", io.BytesIO(file_content), "image/png")}
        response = client.post(f"/api/v1/articles/{article_id}/image", files=files)

        assert response.status_code == 201
        settings = get_settings()
        expected_filename = f"{article_id}_disk_test.png"
        expected_path = os.path.join(settings.upload_dir, expected_filename)
        assert os.path.exists(expected_path), f"File not found at {expected_path}"

    def test_upload_returns_correct_filename(self, client: TestClient) -> None:
        """Uploaded filename should be {article_id}_{original_filename}."""
        article = create_test_article(client)
        article_id = article["id"]

        files = {"file": make_image_file("myimage.png")}
        response = client.post(f"/api/v1/articles/{article_id}/image", files=files)

        assert response.status_code == 201
        data = response.json()
        assert data["filename"] == f"{article_id}_myimage.png"

    def test_upload_returns_correct_url(self, client: TestClient) -> None:
        """Uploaded URL should be /uploads/{article_id}_{original_filename}."""
        article = create_test_article(client)
        article_id = article["id"]

        files = {"file": make_image_file("banner.jpg", content_type="image/jpeg")}
        response = client.post(f"/api/v1/articles/{article_id}/image", files=files)

        assert response.status_code == 201
        data = response.json()
        assert data["url"] == f"/uploads/{article_id}_banner.jpg"

    def test_upload_returns_correct_file_size(self, client: TestClient) -> None:
        """Returned size should match the actual file content length."""
        article = create_test_article(client)
        article_id = article["id"]

        content = b"A" * 512
        files = {"file": ("sized.png", io.BytesIO(content), "image/png")}
        response = client.post(f"/api/v1/articles/{article_id}/image", files=files)

        assert response.status_code == 201
        data = response.json()
        assert data["size"] == 512

    def test_upload_to_nonexistent_article_returns_404(self, client: TestClient) -> None:
        """Uploading to a non-existent article should return 404."""
        files = {"file": make_image_file()}
        response = client.post("/api/v1/articles/99999/image", files=files)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_upload_non_image_file_returns_400(self, client: TestClient) -> None:
        """Uploading a non-image file (text/plain) should return 400."""
        article = create_test_article(client)
        article_id = article["id"]

        files = {"file": ("document.txt", io.BytesIO(b"plain text content"), "text/plain")}
        response = client.post(f"/api/v1/articles/{article_id}/image", files=files)

        assert response.status_code == 400
        assert "image" in response.json()["detail"].lower()

    def test_upload_pdf_returns_400(self, client: TestClient) -> None:
        """Uploading a PDF file should return 400."""
        article = create_test_article(client)
        article_id = article["id"]

        files = {"file": ("report.pdf", io.BytesIO(b"%PDF-content"), "application/pdf")}
        response = client.post(f"/api/v1/articles/{article_id}/image", files=files)

        assert response.status_code == 400

    def test_upload_json_content_type_returns_400(self, client: TestClient) -> None:
        """Uploading with application/json content type should return 400."""
        article = create_test_article(client)
        article_id = article["id"]

        files = {"file": ("data.json", io.BytesIO(b'{"key": "value"}'), "application/json")}
        response = client.post(f"/api/v1/articles/{article_id}/image", files=files)

        assert response.status_code == 400

    def test_image_url_in_article_response_after_upload(self, client: TestClient) -> None:
        """After uploading, GET /articles/{id} should show non-null image_url."""
        article = create_test_article(client)
        article_id = article["id"]

        # Verify image_url is None before upload
        get_resp = client.get(f"/api/v1/articles/{article_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["image_url"] is None

        # Upload image
        files = {"file": make_image_file("photo.png")}
        upload_resp = client.post(f"/api/v1/articles/{article_id}/image", files=files)
        assert upload_resp.status_code == 201

        # Verify image_url is now set
        get_resp_after = client.get(f"/api/v1/articles/{article_id}")
        assert get_resp_after.status_code == 200
        data = get_resp_after.json()
        assert data["image_url"] is not None
        assert data["image_url"].startswith("/uploads/")
        assert str(article_id) in data["image_url"]

    def test_upload_jpeg_content_type_accepted(self, client: TestClient) -> None:
        """image/jpeg content-type should be accepted."""
        article = create_test_article(client)
        article_id = article["id"]

        files = {"file": make_image_file("photo.jpg", b"fake-jpeg", "image/jpeg")}
        response = client.post(f"/api/v1/articles/{article_id}/image", files=files)
        assert response.status_code == 201

    def test_upload_gif_content_type_accepted(self, client: TestClient) -> None:
        """image/gif content-type should be accepted."""
        article = create_test_article(client)
        article_id = article["id"]

        files = {"file": make_image_file("anim.gif", b"GIF89a", "image/gif")}
        response = client.post(f"/api/v1/articles/{article_id}/image", files=files)
        assert response.status_code == 201

    def test_upload_webp_content_type_accepted(self, client: TestClient) -> None:
        """image/webp content-type should be accepted."""
        article = create_test_article(client)
        article_id = article["id"]

        files = {"file": make_image_file("image.webp", b"RIFF....WEBP", "image/webp")}
        response = client.post(f"/api/v1/articles/{article_id}/image", files=files)
        assert response.status_code == 201

    def test_upload_replaces_previous_image_url(self, client: TestClient) -> None:
        """Uploading a second image overwrites image_url with the new one."""
        article = create_test_article(client)
        article_id = article["id"]

        files1 = {"file": make_image_file("first.png")}
        client.post(f"/api/v1/articles/{article_id}/image", files=files1)

        files2 = {"file": make_image_file("second.png")}
        resp2 = client.post(f"/api/v1/articles/{article_id}/image", files=files2)
        assert resp2.status_code == 201

        get_resp = client.get(f"/api/v1/articles/{article_id}")
        assert "second.png" in get_resp.json()["image_url"]


class TestImageDelete:
    """Tests for DELETE /{article_id}/image endpoint."""

    def test_delete_image_returns_204(self, client: TestClient) -> None:
        """Deleting an article image should return 204."""
        article = create_test_article(client)
        article_id = article["id"]

        # Upload first
        files = {"file": make_image_file()}
        client.post(f"/api/v1/articles/{article_id}/image", files=files)

        # Delete
        response = client.delete(f"/api/v1/articles/{article_id}/image")
        assert response.status_code == 204

    def test_delete_image_removes_file_from_disk(self, client: TestClient) -> None:
        """After delete, the image file should not exist on disk."""
        article = create_test_article(client)
        article_id = article["id"]

        files = {"file": ("to_delete.png", io.BytesIO(b"delete-me"), "image/png")}
        upload_resp = client.post(f"/api/v1/articles/{article_id}/image", files=files)
        assert upload_resp.status_code == 201

        settings = get_settings()
        expected_filename = f"{article_id}_to_delete.png"
        expected_path = os.path.join(settings.upload_dir, expected_filename)
        assert os.path.exists(expected_path), "File should exist before delete"

        client.delete(f"/api/v1/articles/{article_id}/image")

        assert not os.path.exists(expected_path), "File should be removed after delete"

    def test_delete_image_clears_image_url(self, client: TestClient) -> None:
        """After delete, GET article should show image_url as None."""
        article = create_test_article(client)
        article_id = article["id"]

        # Upload image
        files = {"file": make_image_file()}
        client.post(f"/api/v1/articles/{article_id}/image", files=files)

        # Confirm image_url is set
        get_resp = client.get(f"/api/v1/articles/{article_id}")
        assert get_resp.json()["image_url"] is not None

        # Delete image
        client.delete(f"/api/v1/articles/{article_id}/image")

        # Confirm image_url is None
        get_resp_after = client.get(f"/api/v1/articles/{article_id}")
        assert get_resp_after.status_code == 200
        assert get_resp_after.json()["image_url"] is None

    def test_delete_image_nonexistent_article_returns_404(self, client: TestClient) -> None:
        """Deleting image for non-existent article should return 404."""
        response = client.delete("/api/v1/articles/99999/image")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_delete_image_when_no_image_set(self, client: TestClient) -> None:
        """Deleting image when article has no image should succeed (204)."""
        article = create_test_article(client)
        article_id = article["id"]

        # No image uploaded — should still return 204
        response = client.delete(f"/api/v1/articles/{article_id}/image")
        assert response.status_code == 204

    def test_delete_image_response_body_is_empty(self, client: TestClient) -> None:
        """204 response should have no body content."""
        article = create_test_article(client)
        article_id = article["id"]

        files = {"file": make_image_file()}
        client.post(f"/api/v1/articles/{article_id}/image", files=files)

        response = client.delete(f"/api/v1/articles/{article_id}/image")
        assert response.status_code == 204
        assert response.content == b""

    def test_delete_twice_is_idempotent(self, client: TestClient) -> None:
        """Deleting an image twice should both return 204 (second has no file to remove)."""
        article = create_test_article(client)
        article_id = article["id"]

        files = {"file": make_image_file()}
        client.post(f"/api/v1/articles/{article_id}/image", files=files)

        # First delete
        r1 = client.delete(f"/api/v1/articles/{article_id}/image")
        assert r1.status_code == 204

        # Second delete — no image_url set, no file on disk
        r2 = client.delete(f"/api/v1/articles/{article_id}/image")
        assert r2.status_code == 204
