import json
import os
from unittest.mock import MagicMock, patch

import pytest
from starlette.testclient import TestClient


@pytest.fixture(scope="module")
def db_setup():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    test_db_url = "sqlite:///./test_suggestions.db"
    engine = create_engine(test_db_url, connect_args={"check_same_thread": False})

    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    yield engine, TestingSessionLocal

    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    if os.path.exists("./test_suggestions.db"):
        os.remove("./test_suggestions.db")


@pytest.fixture
def client(db_setup):
    engine, TestingSessionLocal = db_setup

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def db_session(db_setup):
    engine, TestingSessionLocal = db_setup
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def _seed_article(db_session, title="Test Article", content="Test content"):
    article = Article(title=title, content=content)
    db_session.add(article)
    db_session.commit()
    db_session.refresh(article)
    return article


def _seed_category(db_session, name):
    category = Category(name=name)
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


def _cleanup(db_session):
    db_session.query(Article).delete()
    db_session.query(Category).delete()
    db_session.commit()


def _make_mock_openai_response(suggestions):
    content = json.dumps({"suggestions": suggestions})
    mock_message = MagicMock()
    mock_message.content = content
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    return mock_response


def test_suggest_categories_returns_200_with_suggestions(client, db_session):
    _cleanup(db_session)
    article = _seed_article(db_session, title="AI News", content="About artificial intelligence")
    cat1 = _seed_category(db_session, "Technology")
    cat2 = _seed_category(db_session, "Science")

    suggestions = [
        {"category_id": cat1.id, "category_name": "Technology", "confidence": 0.95},
        {"category_id": cat2.id, "category_name": "Science", "confidence": 0.75},
    ]
    mock_response = _make_mock_openai_response(suggestions)

    with patch("app.ai.classifier.get_openai_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        response = client.get("/api/articles/{}/suggest-categories".format(article.id))

    assert response.status_code == 200
    data = response.json()
    assert "suggestions" in data
    assert len(data["suggestions"]) > 0


def test_suggest_categories_404_for_missing_article(client, db_session):
    _cleanup(db_session)
    response = client.get("/api/articles/999999/suggest-categories")
    assert response.status_code == 404


def test_suggest_categories_empty_when_no_categories(client, db_session):
    _cleanup(db_session)
    article = _seed_article(db_session)

    suggestions = []
    mock_response = _make_mock_openai_response(suggestions)

    with patch("app.ai.classifier.get_openai_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        response = client.get("/api/articles/{}/suggest-categories".format(article.id))

    assert response.status_code == 200
    data = response.json()
    assert data["suggestions"] == []


def test_suggest_categories_limit_parameter(client, db_session):
    _cleanup(db_session)
    article = _seed_article(db_session)
    cat1 = _seed_category(db_session, "Tech")
    cat2 = _seed_category(db_session, "Sports")
    cat3 = _seed_category(db_session, "Health")

    suggestions = [
        {"category_id": cat1.id, "category_name": "Tech", "confidence": 0.9},
        {"category_id": cat2.id, "category_name": "Sports", "confidence": 0.8},
        {"category_id": cat3.id, "category_name": "Health", "confidence": 0.7},
    ]
    mock_response = _make_mock_openai_response(suggestions)

    with patch("app.ai.classifier.get_openai_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        response = client.get("/api/articles/{}/suggest-categories?limit=2".format(article.id))

    assert response.status_code == 200
    data = response.json()
    assert len(data["suggestions"]) <= 2


def test_suggest_categories_default_limit_is_3(client, db_session):
    _cleanup(db_session)
    article = _seed_article(db_session)
    cats = [_seed_category(db_session, "Cat{}".format(i)) for i in range(5)]

    suggestions = [
        {"category_id": c.id, "category_name": "Cat{}".format(i), "confidence": round(0.9 - i * 0.1, 1)}
        for i, c in enumerate(cats)
    ]
    mock_response = _make_mock_openai_response(suggestions)

    with patch("app.ai.classifier.get_openai_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        response = client.get("/api/articles/{}/suggest-categories".format(article.id))

    assert response.status_code == 200
    data = response.json()
    assert len(data["suggestions"]) <= 3


def test_suggest_categories_500_on_llm_api_failure(client, db_session):
    _cleanup(db_session)
    article = _seed_article(db_session)
    _seed_category(db_session, "Tech")

    with patch("app.ai.classifier.get_openai_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("LLM failure")
        mock_get_client.return_value = mock_client

        response = client.get("/api/articles/{}/suggest-categories".format(article.id))

    assert response.status_code == 500


def test_suggest_categories_500_on_malformed_json(client, db_session):
    _cleanup(db_session)
    article = _seed_article(db_session)
    _seed_category(db_session, "Tech")

    mock_message = MagicMock()
    mock_message.content = "not valid json {{{"
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    with patch("app.ai.classifier.get_openai_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        response = client.get("/api/articles/{}/suggest-categories".format(article.id))

    assert response.status_code == 500


def test_suggest_categories_skips_hallucinated_category(client, db_session):
    _cleanup(db_session)
    article = _seed_article(db_session)
    cat1 = _seed_category(db_session, "RealCategory")

    suggestions = [
        {"category_id": cat1.id, "category_name": "RealCategory", "confidence": 0.9},
        {"category_id": 99999, "category_name": "HallucinatedCategory", "confidence": 0.8},
    ]
    mock_response = _make_mock_openai_response(suggestions)

    with patch("app.ai.classifier.get_openai_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        response = client.get("/api/articles/{}/suggest-categories".format(article.id))

    assert response.status_code == 200
    data = response.json()
    category_ids = [s["category_id"] for s in data["suggestions"]]
    assert 99999 not in category_ids


def test_suggest_categories_response_model_fields(client, db_session):
    _cleanup(db_session)
    article = _seed_article(db_session)
    cat1 = _seed_category(db_session, "Technology")

    suggestions = [
        {"category_id": cat1.id, "category_name": "Technology", "confidence": 0.88},
    ]
    mock_response = _make_mock_openai_response(suggestions)

    with patch("app.ai.classifier.get_openai_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        response = client.get("/api/articles/{}/suggest-categories".format(article.id))

    assert response.status_code == 200
    data = response.json()
    assert "suggestions" in data
    assert len(data["suggestions"]) >= 1
    suggestion = data["suggestions"][0]
    assert "category_id" in suggestion
    assert "category_name" in suggestion
    assert "confidence" in suggestion
    assert isinstance(suggestion["confidence"], float)
