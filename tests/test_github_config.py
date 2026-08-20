from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_yaml(path: Path):
    with path.open(encoding="utf-8") as file:
        return yaml.safe_load(file)


def test_github_workflow_and_dependabot_yaml_parse():
    workflow = load_yaml(PROJECT_ROOT / ".github" / "workflows" / "ci.yml")
    dependabot = load_yaml(PROJECT_ROOT / ".github" / "dependabot.yml")

    assert workflow["name"] == "CI"
    assert "test" in workflow["jobs"]
    step_names = [
        step["name"] for step in workflow["jobs"]["test"]["steps"] if "name" in step
    ]
    assert "Build package distributions" in step_names
    assert "Smoke-test installed CLI" in step_names
    assert dependabot["version"] == 2
    assert len(dependabot["updates"]) == 2


def test_issue_forms_have_required_structure():
    template_dir = PROJECT_ROOT / ".github" / "ISSUE_TEMPLATE"
    for name in ("bug_report.yml", "feature_request.yml"):
        form = load_yaml(template_dir / name)
        assert len(form["name"]) > 3
        assert form["description"]
        assert isinstance(form["body"], list)
        assert any(
            field.get("validations", {}).get("required")
            or any(
                option.get("required")
                for option in field.get("attributes", {}).get("options", [])
                if isinstance(option, dict)
            )
            for field in form["body"]
        )

    chooser = load_yaml(template_dir / "config.yml")
    assert chooser["blank_issues_enabled"] is False
