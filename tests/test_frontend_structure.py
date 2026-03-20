"""
Tests for frontend scaffolding structure and content.
Verifies that required frontend files exist and contain expected content.
"""

import json
import os


FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")


def read_file(relative_path: str) -> str:
    """Read a file relative to the frontend directory."""
    full_path = os.path.join(FRONTEND_DIR, relative_path)
    with open(full_path, "r", encoding="utf-8") as f:
        return f.read()


def frontend_path(relative_path: str) -> str:
    """Return absolute path to a frontend file."""
    return os.path.join(FRONTEND_DIR, relative_path)


# ---------------------------------------------------------------------------
# package.json tests
# ---------------------------------------------------------------------------

def test_package_json_exists():
    assert os.path.isfile(frontend_path("package.json"))


def test_package_json_has_react_dependency():
    data = json.loads(read_file("package.json"))
    assert "react" in data["dependencies"]


def test_package_json_has_react_dom_dependency():
    data = json.loads(read_file("package.json"))
    assert "react-dom" in data["dependencies"]


def test_package_json_has_axios_dependency():
    data = json.loads(read_file("package.json"))
    assert "axios" in data["dependencies"]


def test_package_json_has_react_router_dom_dependency():
    data = json.loads(read_file("package.json"))
    assert "react-router-dom" in data["dependencies"]


def test_package_json_has_dev_script():
    data = json.loads(read_file("package.json"))
    assert "dev" in data["scripts"]


def test_package_json_has_build_script():
    data = json.loads(read_file("package.json"))
    assert "build" in data["scripts"]


def test_package_json_has_preview_script():
    data = json.loads(read_file("package.json"))
    assert "preview" in data["scripts"]


def test_package_json_has_typescript_dev_dependency():
    data = json.loads(read_file("package.json"))
    assert "typescript" in data["devDependencies"]


def test_package_json_has_vite_dev_dependency():
    data = json.loads(read_file("package.json"))
    assert "vite" in data["devDependencies"]


# ---------------------------------------------------------------------------
# vite.config.ts tests
# ---------------------------------------------------------------------------

def test_vite_config_exists():
    assert os.path.isfile(frontend_path("vite.config.ts"))


def test_vite_config_has_proxy_to_backend():
    content = read_file("vite.config.ts")
    assert "localhost:8000" in content


def test_vite_config_proxies_api_path():
    content = read_file("vite.config.ts")
    assert "/api" in content


def test_vite_config_uses_react_plugin():
    content = read_file("vite.config.ts")
    assert "react" in content


def test_vite_config_has_define_config():
    content = read_file("vite.config.ts")
    assert "defineConfig" in content


# ---------------------------------------------------------------------------
# tsconfig.json tests
# ---------------------------------------------------------------------------

def test_tsconfig_exists():
    assert os.path.isfile(frontend_path("tsconfig.json"))


def test_tsconfig_has_strict_mode():
    data = json.loads(read_file("tsconfig.json"))
    assert data["compilerOptions"]["strict"] is True


def test_tsconfig_has_jsx_option():
    data = json.loads(read_file("tsconfig.json"))
    assert "jsx" in data["compilerOptions"]


def test_tsconfig_targets_es2020():
    data = json.loads(read_file("tsconfig.json"))
    assert "ES2020" in data["compilerOptions"]["target"]


# ---------------------------------------------------------------------------
# index.html tests
# ---------------------------------------------------------------------------

def test_index_html_exists():
    assert os.path.isfile(frontend_path("index.html"))


def test_index_html_has_root_div():
    content = read_file("index.html")
    assert 'id="root"' in content


def test_index_html_references_main_tsx():
    content = read_file("index.html")
    assert "main.tsx" in content
