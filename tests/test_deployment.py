import sqlite3
import tomllib
from pathlib import Path

import studyforge
from studyforge.dictionary import DictionaryStore
from studyforge.resources import default_cefr_path, default_dictionary_path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_streamlit_deployment_files_are_valid():
    assert (PROJECT_ROOT / "app.py").is_file()
    requirements = (PROJECT_ROOT / "requirements.txt").read_text(encoding="utf-8")
    assert "streamlit==" in requirements
    assert "PyMuPDF==" in requirements
    assert "pytest" not in requirements.lower()

    pyproject = tomllib.loads(
        (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    )
    assert pyproject["project"]["version"] == "0.2.0"
    assert pyproject["project"]["version"] == studyforge.__version__
    assert pyproject["project"]["scripts"]["studyforge"] == "studyforge.cli:main"
    package_data = pyproject["tool"]["setuptools"]["package-data"]["studyforge"]
    assert "data/*.db" in package_data
    assert "data/*.json" in package_data

    config = tomllib.loads(
        (PROJECT_ROOT / ".streamlit" / "config.toml").read_text(encoding="utf-8")
    )
    assert config["server"]["headless"] is True
    assert config["server"]["maxUploadSize"] == 25


def test_bundled_dictionary_is_present_and_valid():
    database = default_dictionary_path()
    assert database.stat().st_size > 1_000_000

    connection = sqlite3.connect(database)
    assert connection.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    connection.close()

    dictionary = DictionaryStore(database)
    assert dictionary.using_fallback is False
    assert dictionary.entry_count >= 50_000
    assert default_cefr_path().stat().st_size > 100_000
