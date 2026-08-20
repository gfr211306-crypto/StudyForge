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


def test_pypi_publish_workflow_uses_oidc_only_in_publish_job():
    path = PROJECT_ROOT / ".github" / "workflows" / "publish.yml"
    workflow = load_yaml(path)
    triggers = workflow.get("on", workflow.get(True))
    build_job = workflow["jobs"]["build"]
    publish_job = workflow["jobs"]["publish"]
    workflow_text = path.read_text(encoding="utf-8").lower()

    assert "workflow_dispatch" in triggers
    assert triggers["release"]["types"] == ["published"]
    assert build_job["permissions"] == {"contents": "read"}
    assert "id-token" not in build_job["permissions"]
    assert publish_job["permissions"] == {"id-token": "write"}
    assert publish_job["environment"]["name"] == "pypi"
    assert publish_job["needs"] == "build"

    build_steps = "\n".join(
        str(step.get("run", "")) + str(step.get("uses", ""))
        for step in build_job["steps"]
    )
    publish_actions = [step.get("uses") for step in publish_job["steps"]]
    assert "python -m build" in build_steps
    assert "python -m twine check dist/*" in build_steps
    assert "actions/upload-artifact@v4" in build_steps
    assert "actions/download-artifact@v4" in publish_actions
    assert "pypa/gh-action-pypi-publish@release/v1" in publish_actions
    assert "password:" not in workflow_text
    assert "api_token" not in workflow_text
    assert "secrets." not in workflow_text


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


def test_external_feedback_issue_form_is_ready_for_human_reports():
    form = load_yaml(
        PROJECT_ROOT / ".github" / "ISSUE_TEMPLATE" / "external_feedback.yml"
    )
    assert form["name"] == "External User Feedback"
    assert "external-user-feedback" in form["labels"]
    assert any(field.get("id") == "tester-id" for field in form["body"])
    assert any(field.get("id") == "workflow" for field in form["body"])
    assert any(field.get("id") == "feedback" for field in form["body"])
