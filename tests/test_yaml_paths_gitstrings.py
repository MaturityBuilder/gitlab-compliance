from src.properties.table_render import render_path_markdown, render_variables_table
from src.properties.yaml_paths import resolve_yaml_path, should_mask_value
from src.modules.gitstrings import extract_gitstrings_blocks, parse_directives, render_fragment


def test_resolve_yaml_path_job_case_insensitive():
    pipeline = {
        "MEGALINTER": {
            "variables": {
                "mode": {"value": "secret-token"},
                "PUBLIC": "visible",
            }
        }
    }
    assert resolve_yaml_path(pipeline, "megalinter.variables.mode") == {
        "value": "secret-token"
    }


def test_render_path_single_job_variable():
    pipeline = {
        "MEGALINTER": {
            "variables": {
                "mode": {"value": "secret-token", "description": "Run mode"},
                "other": {"value": "skip-me"},
            }
        }
    }
    md = render_path_markdown(
        pipeline,
        "megalinter.variables.mode",
        sensitive_paths=["megalinter.variables.mode.value"],
    )
    assert "mode" in md
    assert "secret-token" not in md
    assert "****" in md
    assert "other" not in md
    assert "skip-me" not in md


def test_render_path_parent_variables():
    pipeline = {
        "variables": {"APP": "my-app"},
    }
    md = render_path_markdown(pipeline, "variables")
    assert "APP" in md
    assert "my-app" in md


def test_parse_directives_sensitive_and_path_render():
    raw = """# @render megalinter.variables.mode
# @sensitive megalinter.variables.mode.value
variables:
  APP: ignored
"""
    directives, cleaned = parse_directives(raw)
    assert directives.render == "megalinter.variables.mode"
    assert directives.sensitive == ["megalinter.variables.mode.value"]
    assert "variables:" in cleaned


def test_render_fragment_path_from_ci_file(tmp_path):
    ci = tmp_path / ".gitlab-ci.yml"
    ci.write_text(
        """
MEGALINTER:
  variables:
    mode:
      value: top-secret
    safe:
      value: ok
other-job:
  script: echo hi
# @title Megalinter mode
# @render megalinter.variables.mode
# @sensitive megalinter.variables.mode.value
variables:
  Z: fragment-only
""",
        encoding="utf-8",
    )
    from src.modules.gitstrings import extract_gitstrings_blocks_from_ci_yaml

    block = extract_gitstrings_blocks_from_ci_yaml(ci.read_text(encoding="utf-8"))[-1]
    out = render_fragment(block, keep_source=False, scan_path=ci)
    assert "mode" in out
    assert "top-secret" not in out
    assert "****" in out
    assert "safe" not in out
    assert "Z" not in out


def test_mask_value_path_matching():
    assert should_mask_value(
        "megalinter.variables.mode.value",
        ["megalinter.variables.mode.value"],
    )
    assert should_mask_value(
        "megalinter.variables.mode.value",
        ["MEGALINTER.variables.mode.value"],
    )


def test_render_variables_table_with_prefix_mask():
    table = render_variables_table(
        {"mode": {"value": "hidden"}},
        path_prefix="megalinter.variables",
        sensitive_paths=["megalinter.variables.mode.value"],
    )
    assert "hidden" not in table
    assert "****" in table


def test_scalar_variable_masks_when_sensitive_path_uses_value_suffix():
    table = render_variables_table(
        {"DEFAULT_WORKSPACE": "$CI_PROJECT_DIR"},
        path_prefix="megalinter.variables",
        sensitive_paths=["megalinter.variables.DEFAULT_WORKSPACE.value"],
    )
    assert "$CI_PROJECT_DIR" not in table
    assert "****" in table


def test_render_fragment_multiple_paths_with_sensitive_scalar_variable(tmp_path):
    ci = tmp_path / ".gitlab-ci.yml"
    ci.write_text(
        """# @title Megalinter
# @description
#   Megalinter is a tool that runs a set of linters and formatters on the codebase.
# @render megalinter.artifacts, megalinter.variables
# @sensitive megalinter.variables.DEFAULT_WORKSPACE.value
megalinter:
  script: ["true"]
  variables:
    DEFAULT_WORKSPACE: $CI_PROJECT_DIR
  artifacts:
    when: always
    paths:
      - megalinter-reports
    expire_in: 1 week
  allow_failure: true
  extends:
    - .test:rules
  rules:
    - if: $CI_COMMIT_BRANCH != $CI_DEFAULT_BRANCH && $CI_COMMIT_BRANCH != $CI_COMMIT_TAG
""",
        encoding="utf-8",
    )

    from src.modules.gitstrings import extract_gitstrings_blocks_from_ci_yaml

    block = extract_gitstrings_blocks_from_ci_yaml(ci.read_text(encoding="utf-8"))[0]
    out = render_fragment(block, keep_source=False, scan_path=ci)

    assert "Megalinter" in out
    assert "Source:" in out
    assert ".gitlab-ci.yml#L1-" in out
    assert "Limited render" in out
    assert "Selected variable count: 1 variable" in out
    assert "megalinter-reports" in out
    assert "DEFAULT_WORKSPACE" in out
    assert "$CI_PROJECT_DIR" not in out
    assert "****" in out
    assert "allow_failure" not in out


def test_render_job_rules_explains_ordered_evaluation():
    pipeline = {
        "megalinter": {
            "rules": [
                {
                    "if": "$CI_COMMIT_BRANCH != $CI_DEFAULT_BRANCH",
                    "when": "manual",
                }
            ]
        }
    }

    md = render_path_markdown(pipeline, "megalinter.rules")

    assert "Job rules are evaluated in order" in md
    assert "$CI_COMMIT_BRANCH != $CI_DEFAULT_BRANCH" in md
    assert "manual" in md


def test_render_workflow_rules_explains_pipeline_creation():
    pipeline = {
        "workflow": {
            "rules": [
                {"if": "$CI_PIPELINE_SOURCE == \"merge_request_event\""},
                {"when": "never"},
            ]
        }
    }

    md = render_path_markdown(pipeline, "workflow.rules")

    assert "Workflow rules are evaluated in order" in md
    assert "whether the pipeline runs" in md
    assert "$CI_PIPELINE_SOURCE" in md


def test_render_workflow_block_explains_rules():
    pipeline = {
        "workflow": {
            "name": "MR pipeline",
            "rules": [{"when": "always"}],
        }
    }

    md = render_path_markdown(pipeline, "workflow")

    assert "Workflow rules are evaluated in order" in md
    assert "MR pipeline" in md
