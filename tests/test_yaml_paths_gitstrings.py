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
