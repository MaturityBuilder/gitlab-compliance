from src.modules.gitstrings import (
    parse_directives,
    render_fragment,
)
from src.properties import table_render as tr
from src.properties.table_render import (
    render_includes_table,
    render_inputs_table,
    render_jobs_table,
    render_path_markdown,
    render_variables_table,
)
from src.properties.yaml_paths import (
    SENSITIVE_MASK,
    mask_sensitive_in_structure,
    resolve_yaml_path,
    should_mask_value,
)


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


def test_render_path_variable_value_leaf_uses_parent_key():
    pipeline = {
        "MEGALINTER": {
            "variables": {
                "mode": {"value": "secret-token", "description": "Run mode"},
            }
        }
    }
    md = render_path_markdown(
        pipeline,
        "megalinter.variables.mode.value",
        sensitive_paths=["megalinter.variables.mode.value"],
    )
    assert "| mode |" in md
    assert "| value |" not in md
    assert "secret-token" not in md
    assert "****" in md
    assert "Run mode" in md


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


def test_render_fragment_masks_source_yaml_when_keep_source(tmp_path):
    ci = tmp_path / ".gitlab-ci.yml"
    ci.write_text(
        """
MEGALINTER:
  variables:
    mode:
      value: top-secret
# @title Megalinter mode
# @render megalinter.variables.mode
# @sensitive megalinter.variables.mode.value
megalinter:
  variables:
    mode:
      value: top-secret
""",
        encoding="utf-8",
    )
    from src.modules.gitstrings import extract_gitstrings_blocks_from_ci_yaml

    block = extract_gitstrings_blocks_from_ci_yaml(ci.read_text(encoding="utf-8"))[-1]
    out = render_fragment(block, keep_source=True, scan_path=ci)
    assert "<summary>Source YAML</summary>" in out
    assert "top-secret" not in out
    assert "****" in out


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
                {"if": '$CI_PIPELINE_SOURCE == "merge_request_event"'},
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


def test_resolve_yaml_path_empty_and_none_root():
    assert resolve_yaml_path(None, "a") is None
    assert resolve_yaml_path({"a": 1}, "") is None
    assert resolve_yaml_path({"a": 1}, "   ") is None


def test_resolve_yaml_path_nested_miss_and_non_dict():
    root = {"job": {"stage": "test"}, "scalar": "x"}
    assert resolve_yaml_path(root, "job.missing") is None
    assert resolve_yaml_path(root, "scalar.child") is None
    # Nested miss with job_names=False (index > 0)
    assert resolve_yaml_path(root, "job.MISSING") is None


def test_should_mask_skips_blank_sensitive_entries():
    assert should_mask_value("variables.SECRET", ["", "  ", "variables.SECRET"])
    assert not should_mask_value("variables.SECRET", ["", "  "])


def test_mask_sensitive_structure_all_branches():
    data = {"variables": {"A": "1"}}
    assert mask_sensitive_in_structure(data, "", []) is data

    masked = mask_sensitive_in_structure(
        {"K": {"value": "s", "description": "d"}},
        "variables",
        ["variables.K.value"],
    )
    assert masked["K"]["value"] == SENSITIVE_MASK
    assert masked["K"]["description"] == "d"

    # value_path match, entry uses default (no value key)
    masked = mask_sensitive_in_structure(
        {"K": {"default": "s", "description": "d"}},
        "inputs",
        ["inputs.K"],
    )
    assert masked["K"]["default"] == SENSITIVE_MASK

    # value_path match, neither value nor default → recurse (106-107)
    masked = mask_sensitive_in_structure(
        {"K": {"nested": "s"}},
        "variables",
        ["variables.K"],
    )
    assert isinstance(masked["K"], dict)
    assert masked["K"]["nested"] == "s"

    masked = mask_sensitive_in_structure(
        {"Y": {"default": "hideme", "description": "d"}},
        "spec.inputs",
        ["spec.inputs.Y.default"],
    )
    assert masked["Y"]["default"] == SENSITIVE_MASK
    assert masked["Y"]["description"] == "d"

    masked = mask_sensitive_in_structure(
        {"paths": ["a", "secret"], "PUBLIC": "ok", "SECRET": "tok"},
        "job",
        ["job.SECRET", "job.paths"],
    )
    assert masked["SECRET"] == SENSITIVE_MASK
    assert masked["PUBLIC"] == "ok"
    assert isinstance(masked["paths"], list)

    assert mask_sensitive_in_structure(["x"], "", ["x"]) == ["x"]
    assert mask_sensitive_in_structure("leaf", "p", ["p"]) == "leaf"


def test_resolve_ci_config_path_uses_config_file():
    assert tr._resolve_ci_config_path(None, "pipeline.yml") == "pipeline.yml"
    assert (
        tr._resolve_ci_config_path("/tmp/README.md", "pipeline.yml") == "pipeline.yml"
    )


def test_gitstrings_table_cell_none():
    assert tr._gitstrings_table_cell(None) == ""


def test_entry_field_generic_exception():
    class Boom(dict):
        def __getitem__(self, key):
            raise RuntimeError("broken mapping")

    assert tr._entry_field(Boom(), "description") is None


def test_inputs_row_cells_payload_exception_and_mask():
    table = render_inputs_table(
        {
            "multi": {"default": "d", "type": "string", "description": "x"},
            "num": 42,
            "secret": {"default": "hideme", "description": "s"},
        },
        path_prefix="spec.inputs",
        sensitive_paths=["spec.inputs.secret.default"],
    )
    assert "multi" in table
    assert "42" in table
    assert "hideme" not in table
    assert "****" in table

    class Evil(dict):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._boom = True

        def items(self):
            if self._boom:
                self._boom = False
                raise RuntimeError("items boom")
            return super().items()

    table = render_inputs_table({"bad": Evil({"default": "x", "description": "d"})})
    assert "bad" in table


def test_variables_row_metadata_only_and_exception():
    table = render_variables_table(
        {
            "META_ONLY": {"description": "d", "expand": False},
            "MULTI": {"value": "v", "type": "string", "description": "d"},
        }
    )
    assert "META_ONLY" in table
    assert "MULTI" in table

    class Evil(dict):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._boom = True

        def items(self):
            if self._boom:
                self._boom = False
                raise RuntimeError("items boom")
            return super().items()

    table = render_variables_table({"bad": Evil({"value": "keep", "description": "d"})})
    assert "bad" in table


def test_normalize_include_entries_and_parsed_skip():
    assert tr._normalize_include_entries(None) == []
    assert tr._normalize_include_entries({"local": "x.yml"}) == [{"local": "x.yml"}]
    md = render_includes_table(
        parsed_entries=[
            None,
            {},
            {
                "include_type": "local",
                "project": "x.yml",
                "version": "n/a",
                "valid_version": True,
                "file": "",
                "variables": {},
                "rules": [],
            },
        ]
    )
    assert "x.yml" in md


def test_render_jobs_table_rules_note():
    md = render_jobs_table({"build": {"stage": "test", "rules": [{"when": "always"}]}})
    assert "This job defines `rules`" in md


def test_render_path_include_dict_wrapper():
    pipeline = {"wrap": {"include": {"include": [{"local": "nested.yml"}]}}}
    md = render_path_markdown(pipeline, "wrap.include", include_nested=False)
    assert "local" in md or "nested.yml" in md or "Include" in md


def test_render_path_inputs_default_leaf_and_key():
    pipeline = {
        "spec": {
            "inputs": {
                "env": {"default": "prod", "description": "Environment"},
            }
        }
    }
    md_default = render_path_markdown(pipeline, "spec.inputs.env.default")
    assert "env" in md_default
    assert "prod" in md_default

    md_key = render_path_markdown(pipeline, "spec.inputs.env")
    assert "env" in md_key
    assert "Environment" in md_key
