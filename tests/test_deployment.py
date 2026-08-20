import sqlite3
import tomllib
from pathlib import Path

from studyforge.dictionary import DictionaryStore


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_streamlit_deployment_files_are_valid():
    assert (PROJECT_ROOT / "app.py").is_file()
    requirements = (PROJECT_ROOT / "requirements.txt").read_text(encoding="utf-8")
    assert "streamlit==" in requirements
    assert "PyMuPDF==" in requirements
    assert "pytest" not in requirements.lower()

    config = tomllib.loads(
        (PROJECT_ROOT / ".streamlit" / "config.toml").read_text(encoding="utf-8")
    )
    assert config["server"]["headless"] is True
    assert config["server"]["maxUploadSize"] == 25


def test_bundled_dictionary_is_present_and_valid():
    database = PROJECT_ROOT / "data" / "studyforge_dictionary.db"
    assert database.stat().st_size > 1_000_000

    connection = sqlite3.connect(database)
    assert connection.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    connection.close()

    dictionary = DictionaryStore(database)
    assert dictionary.using_fallback is False
    assert dictionary.entry_count >= 50_000
