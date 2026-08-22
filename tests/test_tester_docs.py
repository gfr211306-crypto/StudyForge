import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEMO_URL = "https://studyforge-kpamprbzckvvgx4sz6fxvz.streamlit.app/"
FEEDBACK_URL = (
    "https://github.com/gfr211306-crypto/StudyForge/issues/new"
    "?template=external_feedback.yml"
)


def read(relative_path: str) -> str:
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def test_readme_links_public_testing_evidence_and_separates_human_testing():
    readme = read("README.md")
    assert "Looking for testers" in readme
    assert "[閱讀 Tester Guide](docs/TESTER_GUIDE.md)" in readme
    assert FEEDBACK_URL in readme
    assert "[CI workflow](.github/workflows/ci.yml)" in readme
    assert "[`tests/`](tests/)" in readme
    assert "Automated runs are never" in readme
    assert "counted as human testers" in readme
    assert "100-case E2E matrix" not in readme
    assert re.search(r"\b\d+\s+pytest tests\b", readme, re.IGNORECASE) is None


def test_tester_guide_has_real_user_flow_links_and_privacy_warning():
    guide = read("docs/TESTER_GUIDE.md")
    for requirement in ("PDF", "IELTS / CEFR", "Export", "Feedback"):
        assert requirement in guide
    assert DEMO_URL in guide
    assert FEEDBACK_URL in guide
    assert "請勿上傳私人、機密或未獲授權的 PDF" in guide


def test_outreach_has_channel_structure_and_public_links():
    outreach = read("docs/TESTER_OUTREACH.md")
    for channel in ("## Reddit", "## Discord", "## GitHub Community / Discussions"):
        assert channel in outreach
    assert DEMO_URL in outreach
    assert FEEDBACK_URL in outreach
    assert "docs/TESTER_GUIDE.md" in outreach


def test_first_three_tester_ids_are_unassigned_scheme_only():
    log = read("docs/HUMAN_FEEDBACK_LOG.md")
    assert "No confirmed human tester records yet." in log
    assert "Tester-001 → Tester-002 → Tester-003" in log
    assert "This line defines the numbering scheme only" in log
    assert "Automated test runs must never be converted into human tester counts." in log
    assert "## Tester-001" not in log
