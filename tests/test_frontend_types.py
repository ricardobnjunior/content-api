"""
Tests for frontend/src/types/index.ts
Verifies that all required TypeScript interfaces are defined.
"""
import os


TYPES_PATH = os.path.join("frontend", "src", "types", "index.ts")


def read_file():
    with open(TYPES_PATH, "r", encoding="utf-8") as f:
        return f.read()


def test_file_exists():
    assert os.path.exists(TYPES_PATH), f"File not found: {TYPES_PATH}"


def test_article_interface_defined():
    content = read_file()
    assert "Article" in content
    assert "interface Article" in content


def test_article_has_id_field():
    content = read_file()
    assert "id:" in content or "id :" in content


def test_article_has_title_field():
    content = read_file()
    assert "title:" in content or "title :" in content


def test_article_has_body_field():
    content = read_file()
    assert "body:" in content or "body :" in content


def test_article_has_image_url_field():
    content = read_file()
    assert "image_url" in content


def test_article_image_url_is_optional():
    content = read_file()
    # Optional field uses ? syntax
    assert "image_url?" in content


def test_create_article_payload_defined():
    content = read_file()
    assert "CreateArticlePayload" in content


def test_update_article_payload_defined():
    content = read_file()
    assert "UpdateArticlePayload" in content


def test_image_response_interface_defined():
    content = read_file()
    assert "ImageResponse" in content
    assert "interface ImageResponse" in content


def test_image_response_has_filename():
    content = read_file()
    assert "filename" in content


def test_image_response_has_url():
    content = read_file()
    assert "url:" in content or "url :" in content


def test_image_response_has_size():
    content = read_file()
    assert "size:" in content or "size :" in content


def test_interfaces_are_exported():
    content = read_file()
    assert "export interface" in content
