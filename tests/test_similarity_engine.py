"""Unit tests for app/ml/similarity.py — the TF-IDF similarity engine."""

import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_similarity.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key")

from app.ml.similarity import (  # noqa: E402
    MIN_SIMILARITY_SCORE,
    SimilarArticle,
    _build_corpus_text,
    find_similar_articles,
)
from app.models.article import Article  # noqa: E402
from app.database import Base  # noqa: E402

# ---------------------------------------------------------------------------
# In-memory database setup
# ---------------------------------------------------------------------------

TEST_DB_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def create_tables():
    """Create all tables before each test and drop them after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db():
    """Provide a test database session."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_article(db, title: str, content: str, status: str = "published") -> Article:
    """Persist and return a test Article."""
    article = Article(title=title, content=content, status=status)
    db.add(article)
    db.commit()
    db.refresh(article)
    return article


# ---------------------------------------------------------------------------
# Tests for _build_corpus_text
# ---------------------------------------------------------------------------

class TestBuildCorpusText:
    """Tests for the internal _build_corpus_text helper."""

    def test_combines_title_and_content(self):
        """Title and content should be joined with a space."""
        article = Article(title="Hello World", content="Some content here.")
        result = _build_corpus_text(article)
        assert result == "Hello World Some content here."

    def test_empty_title_uses_content(self):
        """When title is empty, result should just be the content."""
        article = Article(title="", content="Only content")
        result = _build_corpus_text(article)
        assert result == "Only content"

    def test_empty_content_uses_title(self):
        """When content is empty, result should just be the title."""
        article = Article(title="Only Title", content="")
        result = _build_corpus_text(article)
        assert result == "Only Title"

    def test_none_title_treated_as_empty(self):
        """When title is None, it should be treated as empty string."""
        article = Article(title=None, content="Some content")
        result = _build_corpus_text(article)
        assert "Some content" in result

    def test_none_content_treated_as_empty(self):
        """When content is None, it should be treated as empty string."""
        article = Article(title="Some Title", content=None)
        result = _build_corpus_text(article)
        assert "Some Title" in result

    def test_both_none_returns_empty_string(self):
        """When both title and content are None, result should be empty string."""
        article = Article(title=None, content=None)
        result = _build_corpus_text(article)
        assert result == ""


# ---------------------------------------------------------------------------
# Tests for find_similar_articles
# ---------------------------------------------------------------------------

class TestFindSimilarArticlesEdgeCases:
    """Edge case tests for find_similar_articles."""

    def test_no_published_articles_returns_empty(self, db):
        """With zero published articles, returns empty list."""
        result = find_similar_articles(db, article_id=1, limit=5)
        assert result == []

    def test_single_published_article_returns_empty(self, db):
        """With only one published article, returns empty list."""
        article = make_article(db, "Python Basics", "Variables loops and functions.")
        result = find_similar_articles(db, article_id=article.id, limit=5)
        assert result == []

    def test_article_not_in_published_returns_empty(self, db):
        """If the target article_id is not among published articles, returns empty list."""
        make_article(db, "Article One", "Some content about topic A.")
        make_article(db, "Article Two", "Some content about topic B.")
        result = find_similar_articles(db, article_id=99999, limit=5)
        assert result == []

    def test_draft_articles_excluded(self, db):
        """Draft articles should not appear in results."""
        base = make_article(
            db,
            "Machine Learning Basics",
            "Machine learning uses algorithms to learn from data patterns.",
        )
        draft = make_article(
            db,
            "Machine Learning Advanced",
            "Advanced machine learning techniques use deep neural networks.",
            status="draft",
        )
        make_article(
            db,
            "Machine Learning Tutorial",
            "Machine learning tutorial covers supervised and unsupervised learning.",
        )

        result = find_similar_articles(db, article_id=base.id, limit=10)
        result_ids = [r.id for r in result]
        assert draft.id not in result_ids

    def test_target_article_excluded_from_results(self, db):
        """The target article itself should never appear in results."""
        base = make_article(
            db,
            "Python Programming",
            "Python is a versatile programming language for many applications.",
        )
        make_article(
            db,
            "Python Tutorial",
            "Python programming language tutorial covers core concepts.",
        )

        result = find_similar_articles(db, article_id=base.id, limit=5)
        result_ids = [r.id for r in result]
        assert base.id not in result_ids

    def test_low_similarity_filtered_out(self, db):
        """Articles with cosine similarity below MIN_SIMILARITY_SCORE are excluded."""
        base = make_article(
            db,
            "Quantum Physics Relativity",
            "Quantum mechanics describes subatomic particle behavior and wave functions.",
        )
        make_article(
            db,
            "Pasta Carbonara Recipe",
            "Boil pasta then mix with eggs cheese and pancetta for carbonara.",
        )

        result = find_similar_articles(db, article_id=base.id, limit=5)
        for item in result:
            assert item.similarity_score >= MIN_SIMILARITY_SCORE


class TestFindSimilarArticlesHappyPath:
    """Happy path tests for find_similar_articles."""

    def test_returns_similar_article_instances(self, db):
        """Returns list of SimilarArticle dataclass instances."""
        base = make_article(
            db,
            "Deep Learning Neural Networks",
            "Deep learning uses neural networks with multiple hidden layers for feature extraction.",
        )
        make_article(
            db,
            "Neural Network Deep Learning Guide",
            "Neural networks form the basis of deep learning models used for classification.",
        )

        result = find_similar_articles(db, article_id=base.id, limit=5)
        assert isinstance(result, list)
        if result:
            assert isinstance(result[0], SimilarArticle)
            assert hasattr(result[0], "id")
            assert hasattr(result[0], "title")
            assert hasattr(result[0], "similarity_score")

    def test_results_sorted_descending(self, db):
        """Results should be sorted by similarity_score descending."""
        base = make_article(
            db,
            "Python Machine Learning",
            "Python machine learning uses scikit-learn tensorflow and keras frameworks.",
        )
        make_article(
            db,
            "Python Machine Learning Tutorial",
            "Machine learning in Python with scikit-learn and tensorflow for model training.",
        )
        make_article(
            db,
            "Introduction to Data Science",
            "Data science uses statistics and machine learning for data analysis.",
        )

        result = find_similar_articles(db, article_id=base.id, limit=10)
        scores = [r.similarity_score for r in result]
        assert scores == sorted(scores, reverse=True)

    def test_limit_respected(self, db):
        """Results should not exceed the specified limit."""
        base = make_article(
            db,
            "Python Web Development",
            "Python web development uses Django Flask FastAPI for building REST APIs.",
        )
        for i in range(6):
            make_article(
                db,
                f"Python Web Framework Guide {i}",
                f"Python web framework guide {i} covers Django Flask and FastAPI REST API development.",
            )

        result = find_similar_articles(db, article_id=base.id, limit=3)
        assert len(result) <= 3

    def test_similarity_scores_between_zero_and_one(self, db):
        """All similarity scores should be valid cosine similarity values in [0, 1]."""
        base = make_article(
            db,
            "FastAPI REST API",
            "FastAPI is a modern Python framework for building REST APIs with automatic docs.",
        )
        make_article(
            db,
            "FastAPI Tutorial",
            "Build REST APIs with FastAPI Python framework quickly and efficiently.",
        )

        result = find_similar_articles(db, article_id=base.id, limit=5)
        for item in result:
            assert 0.0 <= item.similarity_score <= 1.0

    def test_only_published_articles_in_results(self, db):
        """Results should only contain published articles."""
        base = make_article(
            db,
            "Python Scripting",
            "Python scripting automates repetitive tasks using scripts and modules.",
        )
        published = make_article(
            db,
            "Python Automation Scripts",
            "Python automation scripts use modules to automate repetitive system tasks.",
        )
        draft = make_article(
            db,
            "Python Scripting Draft",
            "Python scripting draft covers automation and module usage.",
            status="draft",
        )

        result = find_similar_articles(db, article_id=base.id, limit=10)
        result_ids = [r.id for r in result]
        assert draft.id not in result_ids


class TestSimilarArticleDataclass:
    """Tests for the SimilarArticle dataclass."""

    def test_similar_article_creation(self):
        """SimilarArticle should be constructable with id, title, similarity_score."""
        sa = SimilarArticle(id=1, title="Test", similarity_score=0.75)
        assert sa.id == 1
        assert sa.title == "Test"
        assert sa.similarity_score == 0.75

    def test_min_similarity_score_constant(self):
        """MIN_SIMILARITY_SCORE should be 0.1."""
        assert MIN_SIMILARITY_SCORE == 0.1
