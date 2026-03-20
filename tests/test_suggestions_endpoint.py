"""Tests for the AI category suggestions endpoint."""

import json
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.crud.article import create_article
from app.crud.category import create_category


def test_get_suggestions_article_not_found(client):
    """Test 404 when article doesn't exist."""
    response = client.get("/api/v1/suggestions/categories/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Article not found"


def test_get_suggestions_no_categories(client, db):
    """Test empty suggestions when no categories exist."""
    article = create_article(db, title="Test Article", content="Test content")

    response = client.get(f"/api/v1/suggestions/categories/{article.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["article_id"] == article.id
    assert data["suggestions"] == []


def test_get_suggestions_with_llm_response(client, db):
    """Test suggestions returned from LLM."""
    article = create_article(db, title="AI Article", content="About machine learning")
    cat1 = create_category(db, name="Technology")
    cat2 = create_category(db, name="Science")

    mock_suggestions = [
        {"category_name": "Technology", "confidence": 0.92},
        {"category_name": "Science", "confidence": 0.78},
    ]

    with patch("app.api.endpoints.suggestions.classify_article") as mock_classify:
        mock_classify.return_value = mock_suggestions

        response = client.get(f"/api/v1/suggestions/categories/{article.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["article_id"] == article.id
    assert len(data["suggestions"]) == 2
    assert data["suggestions"][0]["category_name"] == "Technology"
    assert data["suggestions"][0]["confidence"] == 0.92
    assert data["suggestions"][0]["category_id"] == cat1.id
    assert data["suggestions"][1]["category_name"] == "Science"
    assert data["suggestions"][1]["confidence"] == 0.78
    assert data["suggestions"][1]["category_id"] == cat2.id


def test_get_suggestions_limit_parameter(client, db):
    """Test that limit parameter restricts number of suggestions."""
    article = create_article(db, title="Test Article", content="Content")
    create_category(db, name="Technology")
    create_category(db, name="Science")
    create_category(db, name="Sports")

    mock_suggestions = [
        {"category_name": "Technology", "confidence": 0.95},
        {"category_name": "Science", "confidence": 0.85},
        {"category_name": "Sports", "confidence": 0.75},
    ]

    with patch("app.api.endpoints.suggestions.classify_article") as mock_classify:
        mock_classify.return_value = mock_suggestions

        response = client.get(f"/api/v1/suggestions/categories/{article.id}?limit=2")

    assert response.status_code == 200
    data = response.json()
    assert len(data["suggestions"]) == 2


def test_get_suggestions_llm_failure(client, db):
    """Test 500 when LLM fails."""
    article = create_article(db, title="Test Article", content="Content")
    create_category(db, name="Technology")

    with patch("app.api.endpoints.suggestions.classify_article") as mock_classify:
        mock_classify.side_effect = Exception("API connection failed")

        response = client.get(f"/api/v1/suggestions/categories/{article.id}")

    assert response.status_code == 500
    assert "LLM classification failed" in response.json()["detail"]


def test_get_suggestions_filters_unknown_categories(client, db):
    """Test that categories not in DB are filtered out."""
    article = create_article(db, title="Test Article", content="Content")
    create_category(db, name="Technology")

    mock_suggestions = [
        {"category_name": "Technology", "confidence": 0.92},
        {"category_name": "UnknownCategory", "confidence": 0.85},
    ]

    with patch("app.api.endpoints.suggestions.classify_article") as mock_classify:
        mock_classify.return_value = mock_suggestions

        response = client.get(f"/api/v1/suggestions/categories/{article.id}")

    assert response.status_code == 200
    data = response.json()
    assert len(data["suggestions"]) == 1
    assert data["suggestions"][0]["category_name"] == "Technology"
