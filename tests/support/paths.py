"""Canonical paths inside the project, resolved from this file's location."""

from __future__ import annotations

from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = TESTS_DIR.parent

CORE_DIR = PROJECT_ROOT / "core"
TEMPLATES_DIR = CORE_DIR / "templates"
STATIC_DIR = CORE_DIR / "static"
VIEWS_DIR = CORE_DIR / "views"
FORMS_DIR = CORE_DIR / "forms"
MODELS_DIR = CORE_DIR / "models"
UTILS_DIR = CORE_DIR / "utils"
THEMES_SOURCE_DIR = PROJECT_ROOT / "themes"
REQUIREMENTS_FILE = PROJECT_ROOT / "requirements.txt"
RUFF_CONFIG = PROJECT_ROOT / "ruff.toml"


def template_files() -> list[Path]:
    """Every Jinja template, sorted for stable test ids."""
    return sorted(TEMPLATES_DIR.rglob("*.html"))


def python_files(*directories: Path) -> list[Path]:
    """Python sources under the given directories (skipping caches)."""
    found: list[Path] = []
    for directory in directories or (CORE_DIR,):
        for path in sorted(directory.rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            found.append(path)
    return found
