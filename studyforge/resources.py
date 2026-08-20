from __future__ import annotations

from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parent
DATA_ROOT = PACKAGE_ROOT / "data"
DEFAULT_DICTIONARY_PATH = DATA_ROOT / "studyforge_dictionary.db"
DEFAULT_CEFR_PATH = DATA_ROOT / "cefr_levels.json"


def default_dictionary_path() -> Path:
    """Return the bundled ECDICT-derived SQLite database path."""
    return DEFAULT_DICTIONARY_PATH


def default_cefr_path() -> Path:
    """Return the bundled unambiguous CEFR word mapping path."""
    return DEFAULT_CEFR_PATH
