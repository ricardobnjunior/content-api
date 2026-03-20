"""
Tests for frontend/src/api/articles.ts
Verifies that all required functions exist in the implementation.
"""
import os


ARTICLES_TS_PATH = os.path.join("frontend", "src", "api", "articles.ts")


def read_file():
    with open(ARTICLES_TS_PATH, "r", encoding="utf-8") as f:
        return f.read()


def test_file_exists():
    assert os.path.exists(ARTICLES_TS_PATH), f"File not found: {ARTICLES_TS_PATH}"


def test_imports_api_client():
    content = read_file()
    assert "apiClient" in content
    assert "./client" in content


def test_imports_types():
    content = read_file()
    assert "Article" in content
    assert "CreateArticlePayload" in content
    assert "UpdateArticlePayload" in content
    assert "ImageResponse" in content


def test_get_articles_function_exists():
    content = read_file()
    assert "getArticles" in content
    assert "/api/v1/articles" in content


def test_get_article_function_exists():
    content = read_file()
    assert "getArticle" in content


def test_create_article_function_exists():
    content = read_file()
    assert "createArticle" in content


def test_update_article_function_exists():
    content = read_file()
    assert "updateArticle" in content


def test_delete_article_function_exists():
    content = read_file()
    assert "deleteArticle" in content


def test_upload_article_image_function_exists():
    content = read_file()
    assert "uploadArticleImage" in content


def test_upload_article_image_uses_formdata():
    content = read_file()
    assert "FormData" in content
    assert 'fd.append("file"' in content or "fd.append('file'" in content


def test_upload_article_image_uses_multipart_header():
    content = read_file()
    assert "multipart/form-data" in content


def test_upload_article_image_posts_to_correct_endpoint():
    content = read_file()
    assert "/image" in content
    assert "articleId" in content


def test_delete_article_image_function_exists():
    content = read_file()
    assert "deleteArticleImage" in content


def test_delete_article_image_calls_delete():
    content = read_file()
    # Should call apiClient.delete with the image endpoint
    assert "apiClient.delete" in content
    assert "/image" in content


def test_upload_returns_image_response_type():
    content = read_file()
    assert "ImageResponse" in content
    # The function should return a Promise of ImageResponse
    assert "Promise<ImageResponse>" in content
