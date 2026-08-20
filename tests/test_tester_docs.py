from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def read(relative_path: str) -> str:
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def test_readme_separates_human_and_automated_testing():
    readme = read("README.md")
    assert "Looking for testers" in readme
    assert "3 位真實外部測試者" in readme
    assert "約 **5 分鐘**" in readme
    assert "**Human testers:** 0 confirmed" in readme
    assert "**Automated validation:** 100-case E2E matrix and 32 pytest tests" in readme


def test_tester_guide_has_minimum_real_user_flow():
    guide = read("docs/TESTER_GUIDE.md")
    for requirement in ("PDF", "IELTS / CEFR", "Export", "Feedback"):
        assert requirement in guide
    assert "10–15" not in guide
    assert "No Star" in guide


def test_outreach_has_three_short_channel_posts_and_preflight():
    outreach = read("docs/TESTER_OUTREACH.md")
    for channel in ("## Reddit", "## Discord", "## GitHub Community / Discussions"):
        assert channel in outreach
    assert "Looking for 3" in outreach
    assert "5 minutes" in outreach
    assert "No Star" in outreach
    assert "無痕" in outreach


def test_first_three_tester_ids_are_unassigned_scheme_only():
    log = read("docs/HUMAN_FEEDBACK_LOG.md")
    assert "No confirmed human tester records yet." in log
    assert "Tester-001 → Tester-002 → Tester-003" in log
    assert "This line defines the numbering scheme only" in log
    assert "## Tester-001" not in log
