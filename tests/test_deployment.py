import os
import shutil
import sqlite3
import subprocess
import sys
import tomllib
from pathlib import Path

import studyforge
from studyforge.dictionary import DictionaryStore
from studyforge.resources import default_cefr_path, default_dictionary_path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_streamlit_deployment_files_are_valid():
    assert (PROJECT_ROOT / "app.py").is_file()
    app_source = (PROJECT_ROOT / "app.py").read_text(encoding="utf-8")
    assert "use_container_width" not in app_source
    requirements = (PROJECT_ROOT / "requirements.txt").read_text(encoding="utf-8")
    assert "streamlit==" in requirements
    assert "PyMuPDF==" in requirements
    assert "pytest" not in requirements.lower()
    assert "-e ." in requirements.splitlines()

    pyproject = tomllib.loads(
        (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    )
    project_version = pyproject["project"]["version"]
    assert project_version == studyforge.__version__
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


def test_app_imports_when_checkout_directory_shadows_package(tmp_path):
    checkout = tmp_path / "studyforge"
    checkout.mkdir()
    shutil.copy2(PROJECT_ROOT / "app.py", checkout / "app.py")
    shutil.copytree(
        PROJECT_ROOT / "studyforge",
        checkout / "studyforge",
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )

    environment = os.environ.copy()
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import runpy; "
                f"runpy.run_path({str(checkout / 'app.py')!r}, "
                "run_name='streamlit_import_test')"
            ),
        ],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
