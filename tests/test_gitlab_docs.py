from pathlib import Path

import pytest

from gitlab_docs.pipeline import generate_documentation_body
from gitlab_docs.reset_docs import merge_markdown_output
from gitlab_docs.constants import GLDOCS_CLOSING_MARKER, GLDOCS_OPENING_MARKER
from gitlab_docs.variables import build_variables_section
from gitlab_docs.workflows import _workflow_rule_entries, build_workflows_section


ROOT = Path(__file__).resolve().parents[1]
SAMPLE_CI = ROOT / "sample-files" / ".gitlab-ci.yml"
REPO_CI = ROOT / ".gitlab-ci.yml"


def test_variables_section_lists_every_key():
    data = {
        "variables": {
            "RUNNER": "docker",
            "APPLICATION": {
                "value": "gitlab-docs",
                "description": "App name",
            },
        }
    }
    body = build_variables_section(data)
    assert "RUNNER" in body
    assert "APPLICATION" in body
    assert "App name" in body


def test_workflow_rules_dict_form():
    data = {
        "workflow": {
            "rules": [
                {"if": '$CI_PIPELINE_SOURCE == "merge_request_event"'},
                {"when": "never"},
            ]
        }
    }
    assert len(_workflow_rule_entries(data["workflow"])) == 2
    body = build_workflows_section(data)
    assert "Workflow" in body
    assert "merge_request_event" in body


def test_workflow_rules_list_form():
    data = {"workflow": [{"if": '$CI_COMMIT_BRANCH == "main"'}, {"when": "never"}]}
    body = build_workflows_section(data)
    assert body.count("Workflow Rules") >= 1


def test_sample_includes_and_jobs():
    body = generate_documentation_body(SAMPLE_CI)
    assert "Includes" in body or "include" in body.lower()
    assert "BUILD" in body or "build" in body


def test_repo_ci_generates_jobs():
    body = generate_documentation_body(REPO_CI)
    assert "MEGALINTER" in body


def test_markdown_merge_replaces_generated_block(tmp_path):
    target = tmp_path / "docs.md"
    wrapped = merge_markdown_output(target, "new body")
    assert "new body" in wrapped
    assert GLDOCS_OPENING_MARKER in wrapped
    assert GLDOCS_CLOSING_MARKER in wrapped

    original = (
        "# Readme\n\n"
        f"{GLDOCS_OPENING_MARKER}\n\nold\n\n{GLDOCS_CLOSING_MARKER}\n\nfooter\n"
    )
    start = original.find(GLDOCS_OPENING_MARKER)
    end = original.rfind(GLDOCS_CLOSING_MARKER) + len(GLDOCS_CLOSING_MARKER)
    replacement = (
        f"{GLDOCS_OPENING_MARKER}\n\nnew body\n\n{GLDOCS_CLOSING_MARKER}\n"
    )
    result = original[:start] + replacement.strip() + original[end:]
    assert "old" not in result
    assert "new body" in result
    assert "footer" in result


def test_detailed_includes_workflow_for_repo():
    body = generate_documentation_body(REPO_CI, document_workflows=True)
    assert "Workflow" in body


@pytest.mark.parametrize("fmt", ["markdown", "html", "json", "csv"])
def test_output_formats(fmt):
    from gitlab_docs.render import DocTable, render_table

    table = DocTable(headers=["Key", "Value"], rows=[["MEGALINTER", "true"]])
    out = render_table(table, fmt)
    assert out.strip()
    if fmt == "html":
        assert "<table" in out.lower()
    if fmt == "json":
        assert "MEGALINTER" in out or "[" in out or "{" in out