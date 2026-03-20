"""Tests to verify that README.md exists and contains required documentation sections."""

from pathlib import Path


README_PATH = Path(__file__).parent.parent / "README.md"


def test_readme_exists() -> None:
    """Verify that README.md exists at the repository root."""
    assert README_PATH.exists(), "README.md must exist at the repository root"
    assert README_PATH.is_file(), "README.md must be a regular file"


def test_readme_has_content() -> None:
    """Verify that README.md is not empty."""
    content = README_PATH.read_text(encoding="utf-8")
    assert len(content.strip()) > 0, "README.md must not be empty"


def test_readme_has_project_title() -> None:
    """Verify that README.md has a top-level markdown heading (project name)."""
    content = README_PATH.read_text(encoding="utf-8")
    lines = content.splitlines()
    h1_lines = [line for line in lines if line.startswith("# ")]
    assert len(h1_lines) >= 1, "README.md must have at least one top-level heading (# Title)"


def test_readme_has_installation_instructions() -> None:
    """Verify that README.md contains installation instructions."""
    content = README_PATH.read_text(encoding="utf-8").lower()
    assert "install" in content or "pip" in content, (
        "README.md must contain installation instructions (e.g., 'install' or 'pip')"
    )


def test_readme_has_api_endpoints() -> None:
    """Verify that README.md documents API endpoints."""
    content = README_PATH.read_text(encoding="utf-8")
    assert "GET" in content or "POST" in content or "/api" in content, (
        "README.md must contain API endpoint documentation (GET, POST, or /api)"
    )


def test_readme_has_run_instructions() -> None:
    """Verify that README.md contains instructions for running the server."""
    content = README_PATH.read_text(encoding="utf-8").lower()
    assert "uvicorn" in content or "run" in content, (
        "README.md must contain run instructions (e.g., 'uvicorn' or 'run')"
    )


def test_readme_has_test_instructions() -> None:
    """Verify that README.md contains instructions for running tests."""
    content = README_PATH.read_text(encoding="utf-8").lower()
    assert "pytest" in content, (
        "README.md must contain test instructions (e.g., 'pytest')"
    )


def test_readme_has_project_structure() -> None:
    """Verify that README.md documents the project structure."""
    content = README_PATH.read_text(encoding="utf-8").lower()
    assert "structure" in content or "app/" in content or "tests/" in content, (
        "README.md must contain a project structure section"
    )


def test_readme_has_technologies_section() -> None:
    """Verify that README.md lists the technologies used."""
    content = README_PATH.read_text(encoding="utf-8").lower()
    assert "fastapi" in content or "sqlalchemy" in content, (
        "README.md must mention the technologies used (FastAPI or SQLAlchemy)"
    )


def test_readme_has_curl_examples() -> None:
    """Verify that README.md contains curl usage examples."""
    content = README_PATH.read_text(encoding="utf-8").lower()
    assert "curl" in content, (
        "README.md must contain curl usage examples"
    )


def test_readme_mentions_python_version() -> None:
    """Verify that README.md mentions the required Python version."""
    content = README_PATH.read_text(encoding="utf-8")
    assert "Python" in content or "python" in content, (
        "README.md must mention the Python version requirement"
    )


def test_readme_is_valid_markdown() -> None:
    """Verify that README.md uses basic markdown formatting."""
    content = README_PATH.read_text(encoding="utf-8")
    has_heading = any(line.startswith("#") for line in content.splitlines())
    assert has_heading, "README.md must use markdown headings (lines starting with #)"


def test_readme_not_placeholder() -> None:
    """Verify that README.md is not a generic placeholder."""
    content = README_PATH.read_text(encoding="utf-8").lower()
    placeholder_phrases = ["todo", "coming soon", "placeholder", "lorem ipsum"]
    for phrase in placeholder_phrases:
        assert phrase not in content, (
            f"README.md appears to be a placeholder — found '{phrase}'"
        )
