from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_app_starts_and_shows_uploader():
    app_path = Path(__file__).resolve().parents[1] / "app.py"
    app = AppTest.from_file(app_path, default_timeout=15)
    app.run()
    assert not app.exception
    assert len(app.file_uploader) == 1
    assert "上傳教材" in [heading.value for heading in app.subheader]
