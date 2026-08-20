from pathlib import Path

from streamlit.testing.v1 import AppTest

from app import BUG_REPORT_URL, FEATURE_REQUEST_URL, safe_download_name


def test_app_starts_and_shows_uploader():
    app_path = Path(__file__).resolve().parents[1] / "app.py"
    app = AppTest.from_file(app_path, default_timeout=15)
    app.run()
    assert not app.exception
    assert len(app.file_uploader) == 1
    assert "上傳教材" in [heading.value for heading in app.subheader]


def test_feedback_links_target_github_issue_templates():
    assert BUG_REPORT_URL == (
        "https://github.com/gfr211306-crypto/StudyForge/issues/new"
        "?template=bug_report.yml"
    )
    assert FEATURE_REQUEST_URL == (
        "https://github.com/gfr211306-crypto/StudyForge/issues/new"
        "?template=feature_request.yml"
    )


def test_download_name_removes_path_and_unsafe_characters():
    assert safe_download_name("../../My lesson <final>.pdf") == "My_lesson_final_anki.csv"
