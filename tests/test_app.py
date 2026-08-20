from pathlib import Path

from streamlit.testing.v1 import AppTest

from app import safe_download_name


def test_app_starts_and_shows_uploader():
    app_path = Path(__file__).resolve().parents[1] / "app.py"
    app = AppTest.from_file(app_path, default_timeout=15)
    app.run()
    assert not app.exception
    assert len(app.file_uploader) == 1
    assert "上傳教材" in [heading.value for heading in app.subheader]


def test_download_name_removes_path_and_unsafe_characters():
    assert safe_download_name("../../My lesson <final>.pdf") == "My_lesson_final_anki.csv"
