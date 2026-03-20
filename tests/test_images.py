"""Tests for article image upload and delete endpoints."""

import io
import os

import pytest
from fastapi.testclient import TestClient


def create_test_article(client: TestClient) -> dict:
    """Create a test article and return its JSON representation.

    Args:
        client: FastAPI test client.

    Returns:
        Article response dictionary.
    """
    response = client.post(
        "/api/v1/articles/",
        json={"title": "Test Article", "content": "Test content", "status": "draft"},
    )
    assert response.status_code == 201
    return response.json()


def test_upload_valid_image(client: TestClient) -> None:
    """Test uploading a valid image file returns 201 with ImageResponse fields."""
    article = create_test_article(client)
    article_id = article["id"]

    image_content = b"\xff\xd8\xff\xe0" + b"\x00" * 100
    files = {
        "file": ("test_image.jpg", io.BytesIO(image_content), "image/jpeg"),
    }

    response = client.post(f"/api/v1/articles/{article_id}/image", files=files)

    assert response.status_code == 201
    data = response.json()
    assert "filename" in data
    assert "url" in data
    assert "size" in data
    assert data["filename"] == f"{article_id}_test_image.jpg"
    assert data["url"] == f"/uploads/{article_id}_test_image.jpg"
    assert data["size"] == len(image_content)


def test_upload_nonexistent_article(client: TestClient) -> None:
    """Test uploading an image to a non-existent article returns 404."""
    image_content = b"\xff\xd8\xff\xe0" + b"\x00" * 50
    files = {
        "file": ("photo.jpg", io.BytesIO(image_content), "image/jpeg"),
    }

    response = client.post("/api/v1/articles/99999/image", files=files)

    assert response.status_code == 404
    assert response.json()["detail"] == "Article not found"


def test_upload_non_image_file(client: TestClient) -> None:
    """Test uploading a non-image file returns 400."""
    article = create_test_article(client)
    article_id = article["id"]

    text_content = b"This is a plain text file, not an image."
    files = {
        "file": ("document.txt", io.BytesIO(text_content), "text/plain"),
    }

    response = client.post(f"/api/v1/articles/{article_id}/image", files=files)

    assert response.status_code == 400
    assert "image" in response.json()["detail"].lower()


def test_image_url_in_article_response(client: TestClient) -> None:
    """Test that image_url appears in article GET response after upload."""
    article = create_test_article(client)
    article_id = article["id"]

    image_content = b"\x89PNG\r\n\x1a\n" + b"\x00" * 80
    files = {
        "file": ("banner.png", io.BytesIO(image_content), "image/png"),
    }

    upload_response = client.post(f"/api/v1/articles/{article_id}/image", files=files)
    assert upload_response.status_code == 201

    get_response = client.get(f"/api/v1/articles/{article_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["image_url"] is not None
    assert data["image_url"] == f"/uploads/{article_id}_banner.png"


def test_delete_image(client: TestClient) -> None:
    """Test deleting an article image removes file from disk and clears image_url."""
    from app.config import get_settings

    article = create_test_article(client)
    article_id = article["id"]

    image_content = b"\xff\xd8\xff\xe0" + b"\x00" * 60
    files = {
        "file": ("cover.jpg", io.BytesIO(image_content), "image/jpeg"),
    }

    upload_response = client.post(f"/api/v1/articles/{article_id}/image", files=files)
    assert upload_response.status_code == 201

    settings = get_settings()
    expected_filename = f"{article_id}_cover.jpg"
    filepath = os.path.join(settings.upload_dir, expected_filename)
    assert os.path.exists(filepath), "File should exist on disk after upload"

    delete_response = client.delete(f"/api/v1/articles/{article_id}/image")
    assert delete_response.status_code == 204

    assert not os.path.exists(filepath), "File should be removed from disk after delete"

    get_response = client.get(f"/api/v1/articles/{article_id}")
    assert get_response.status_code == 200
    assert get_response.json()["image_url"] is None


def test_delete_image_nonexistent_article(client: TestClient) -> None:
    """Test deleting image from a non-existent article returns 404."""
    response = client.delete("/api/v1/articles/99999/image")
    assert response.status_code == 404


def test_delete_image_no_file(client: TestClient) -> None:
    """Test deleting image on article that never had one returns 204 gracefully."""
    article = create_test_article(client)
    article_id = article["id"]

    response = client.delete(f"/api/v1/articles/{article_id}/image")
    assert response.status_code == 204


def test_upload_png_image(client: TestClient) -> None:
    """Test uploading a PNG image works correctly."""
    article = create_test_article(client)
    article_id = article["id"]

    png_content = b"\x89PNG\r\n\x1a\n" + b"\x00" * 120
    files = {
        "file": ("photo.png", io.BytesIO(png_content), "image/png"),
    }

    response = client.post(f"/api/v1/articles/{article_id}/image", files=files)

    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == f"{article_id}_photo.png"
    assert data["url"] == f"/uploads/{article_id}_photo.png"
    assert data["size"] == len(png_content)


def test_upload_gif_image(client: TestClient) -> None:
    """Test uploading a GIF image (image/gif content type) works correctly."""
    article = create_test_article(client)
    article_id = article["id"]

    gif_content = b"GIF89a" + b"\x00" * 50
    files = {
        "file": ("animation.gif", io.BytesIO(gif_content), "image/gif"),
    }

    response = client.post(f"/api/v1/articles/{article_id}/image", files=files)

    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == f"{article_id}_animation.gif"


def test_upload_saves_file_to_disk(client: TestClient) -> None:
    """Test that uploading an image actually saves the file to the upload directory."""
    from app.config import get_settings

    article = create_test_article(client)
    article_id = article["id"]

    image_content = b"\xff\xd8\xff\xe0" + b"\x00" * 200
    files = {
        "file": ("disk_test.jpg", io.BytesIO(image_content), "image/jpeg"),
    }

    response = client.post(f"/api/v1/articles/{article_id}/image", files=files)
    assert response.status_code == 201

    settings = get_settings()
    expected_path = os.path.join(settings.upload_dir, f"{article_id}_disk_test.jpg")
    assert os.path.exists(expected_path)

    with open(expected_path, "rb") as f:
        saved_content = f.read()
    assert saved_content == image_content


def test_upload_replaces_previous_image(client: TestClient) -> None:
    """Test that uploading a second image updates image_url to the new file."""
    article = create_test_article(client)
    article_id = article["id"]

    first_content = b"\xff\xd8\xff\xe0" + b"\x00" * 50
    files1 = {"file": ("first.jpg", io.BytesIO(first_content), "image/jpeg")}
    r1 = client.post(f"/api/v1/articles/{article_id}/image", files=files1)
    assert r1.status_code == 201

    second_content = b"\xff\xd8\xff\xe0" + b"\x00" * 80
    files2 = {"file": ("second.jpg", io.BytesIO(second_content), "image/jpeg")}
    r2 = client.post(f"/api/v1/articles/{article_id}/image", files=files2)
    assert r2.status_code == 201

    get_response = client.get(f"/api/v1/articles/{article_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["image_url"] == f"/uploads/{article_id}_second.jpg"


def test_upload_application_octet_stream_rejected(client: TestClient) -> None:
    """Test that application/octet-stream content type is rejected."""
    article = create_test_article(client)
    article_id = article["id"]

    binary_content = b"\x00\x01\x02\x03\x04"
    files = {
        "file": ("binary.bin", io.BytesIO(binary_content), "application/octet-stream"),
    }

    response = client.post(f"/api/v1/articles/{article_id}/image", files=files)
    assert response.status_code == 400


def test_article_image_url_none_by_default(client: TestClient) -> None:
    """Test that a newly created article has image_url as None."""
    article = create_test_article(client)
    assert article["image_url"] is None
