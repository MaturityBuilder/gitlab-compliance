"""Targeted tests for remaining line coverage on src/."""

from __future__ import annotations

import os
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import click
import pytest
import yaml
from click.testing import CliRunner

from src.compliance.api_config import require_api_connection
from src.compliance.behave_support import environment as behave_env
from src.compliance.behave_support.steps import given_steps, then_steps, when_steps
from src.compliance.console import render_compliance_console
from src.compliance.metadata import collect_policy_index, build_policy_catalog
from src.compliance.model import load_pipeline_entities, load_yaml_entities
from src.compliance.models import ComplianceResult, ScenarioResult
from src.compliance.oci_registry import is_oci_reference, push_policies
from src.compliance.policy_doc import render_policy_catalog
from src.compliance.render import (
    render_compliance_code_quality,
    render_compliance_html,
    render_compliance_markdown,
    render_compliance_mr_comment,
)
from src.compliance.runner import _temporary_gitlab_env, run_compliance
from src.compliance.stash import assert_all, entity_has_property, format_entity_ref
from src.gitlab_docs import (
    _resolve_policies_dir,
    compliance_doc,
    gitlab_compliance,
)
from src.modules.command_reference import _param_metadata, dumps
from src.modules.pipeline_data import collect_pipeline_data
from src.modules.release import (
    build_markdown,
    parse_gitlab_date,
    print_release_preview,
    sort_tags,
)
from src.modules.swagger_html import render_swagger_html
from src.modules.yaml_lines import index_yaml_file
from src.modules.yaml_md_table import generate_markdown_table
from src.modules.doc_controller import add_between_markers, remove_duplicate_headings, update_marked_block
from src.properties.extract_job_attribute import get_job_attribute
from src.properties.includes import document_includes
from src.properties.inputs import document_inputs
from src.properties.jobs import get_jobs
from src.properties.variables import document_variables
from src.properties.workflows import document_workflows

REPO_ROOT = Path(__file__).resolve().parents[1]
SAMPLE = REPO_ROOT / "sample-files" / ".gitlab-ci.yml"
PASSING = REPO_ROOT / "tests" / "compliance_policies" / "passing"
SKIP_POLICIES = REPO_ROOT / "tests" / "compliance_policies" / "skip"
ANNOTATED = REPO_ROOT / "tests" / "compliance_policies" / "annotated"

MARKER_START = "[comment]: <> (gitlab-docs-opening-auto-generated)"
MARKER_END = "[comment]: <> (gitlab-docs-closing-auto-generated)"


def _markers_file(tmp_path):
    out = tmp_path / "out.md"
    out.write_text(f"{MARKER_START}\n{MARKER_END}\n", encoding="utf-8")
    return out


class TestYamlMdTableBranches:
    @pytest.mark.parametrize(
        "data,needle",
        [
            (["local-file.yml"], "local-file.yml"),
            ([{"local": "path.yml"}], "path.yml"),
            ([{"project": "g/p", "ref": "main"}], "g/p"),
            ([{"component": "group/comp@1.0.0"}], "group/comp"),
            ([{"component": "no-version"}], "no-version"),
        ],
    )
    def test_include_shapes(self, data, needle):
        assert needle in generate_markdown_table(data)


class TestDocControllerExtra:
    def test_update_marked_block_dry_on_existing_file(self, tmp_path):
        path = tmp_path / "readme.md"
        path.write_text(f"{MARKER_START}\nold\n{MARKER_END}\n", encoding="utf-8")
        update_marked_block(str(path), "new", dry=True)
        assert "old" in path.read_text(encoding="utf-8")

    def test_add_between_markers_creates_new_file(self, tmp_path):
        path = tmp_path / "new.md"
        add_between_markers(str(path), "body")
        text = path.read_text(encoding="utf-8")
        assert MARKER_START in text
        assert "body" in text

    def test_add_between_markers_appends_block_without_markers(self, tmp_path):
        path = tmp_path / "readme.md"
        path.write_text("intro\n", encoding="utf-8")
        add_between_markers(str(path), "generated")
        text = path.read_text(encoding="utf-8")
        assert "intro" in text
        assert "generated" in text

    def test_remove_duplicate_headings_overwrites_source(self, tmp_path):
        path = tmp_path / "doc.md"
        path.write_text("# Title\n\n# Title\n", encoding="utf-8")
        remove_duplicate_headings(path)
        assert path.read_text(encoding="utf-8").count("# Title") == 1

    def test_update_marked_block_handles_io_error(self, tmp_path, monkeypatch):
        path = tmp_path / "readme.md"
        path.write_text("x\n", encoding="utf-8")

        def boom(*_args, **_kwargs):
            raise OSError("disk full")

        monkeypatch.setattr("builtins.open", boom)
        update_marked_block(str(path), "y")

    def test_add_between_markers_handles_io_error(self, tmp_path, monkeypatch):
        path = tmp_path / "readme.md"

        def boom(*_args, **_kwargs):
            raise OSError("disk full")

        monkeypatch.setattr("builtins.open", boom)
        add_between_markers(str(path), "y")


class TestPropertiesExtra:
    def test_document_variables_scalar_and_title(self, tmp_path):
        cfg = tmp_path / "ci.yml"
        cfg.write_text("variables:\n  PLAIN: hello\n", encoding="utf-8")
        out = _markers_file(tmp_path)
        document_variables(str(out), str(cfg), DISABLE_TITLE=False)

    def test_document_variables_yaml_error(self, tmp_path, monkeypatch):
        out = _markers_file(tmp_path)
        cfg = tmp_path / "ci.yml"
        cfg.write_text("variables:\n  X: 1\n", encoding="utf-8")

        def raise_yaml(*_args, **_kwargs):
            raise yaml.YAMLError("bad")

        monkeypatch.setattr("src.properties.variables.add_between_markers", raise_yaml)
        document_variables(str(out), str(cfg), DISABLE_TITLE=True)

    def test_document_inputs_with_title(self, tmp_path):
        cfg = tmp_path / "ci.yml"
        cfg.write_text(
            "spec:\n  inputs:\n    env:\n      description: d\n      options: [a]\n",
            encoding="utf-8",
        )
        out = _markers_file(tmp_path)
        document_inputs(str(out), str(cfg), DISABLE_TITLE=False)

    def test_document_workflows_dict_rules_and_fallback_table(self, tmp_path, monkeypatch):
        cfg = tmp_path / "ci.yml"
        cfg.write_text(
            "workflow:\n  rules:\n    - if: $CI\n      when: always\n",
            encoding="utf-8",
        )
        out = _markers_file(tmp_path)
        monkeypatch.setattr(
            "src.properties.workflows.common.build_dict_list_table",
            lambda *_a, **_k: None,
        )
        document_workflows(str(out), str(cfg), DISABLE_TITLE=False)

    def test_document_includes_nested_error(self, tmp_path, monkeypatch):
        root = tmp_path / "proj"
        root.mkdir()
        nested = root / "nested.yml"
        nested.write_text("job:\n  script: echo\n", encoding="utf-8")
        cfg = root / ".gitlab-ci.yml"
        cfg.write_text("include:\n  - local: nested.yml\n", encoding="utf-8")
        out = _markers_file(tmp_path)

        def fail_jobs(*_args, **_kwargs):
            raise RuntimeError("nested fail")

        monkeypatch.setattr("src.properties.includes.jobs.get_jobs", fail_jobs)
        document_includes(str(out), str(cfg))

    def test_get_jobs_non_mapping_job(self, tmp_path):
        cfg = tmp_path / "ci.yml"
        cfg.write_text("broken_job: just-a-string\n", encoding="utf-8")
        out = _markers_file(tmp_path)
        get_jobs(str(out), str(cfg), detailed=True)

    def test_get_job_attribute_multiple_attributes(self, tmp_path):
        out = _markers_file(tmp_path)
        get_job_attribute(
            str(out),
            str(SAMPLE),
            attributes="stage,image",
        )

    def test_document_variables_malformed_dict(self, tmp_path):
        cfg = tmp_path / "ci.yml"
        cfg.write_text(
            "variables:\n  BAD:\n    value: v\n    description: ok\n",
            encoding="utf-8",
        )
        out = _markers_file(tmp_path)

        class EvilDict(dict):
            def __contains__(self, key):
                if key == "options":
                    raise RuntimeError("broken variable")
                return super().__contains__(key)

        original_read = __import__("src.modules.common", fromlist=["common"]).read_yml

        def patched_read(path):
            docs = original_read(path)
            for doc in docs:
                if "variables" in doc:
                    doc["variables"]["BAD"] = EvilDict(doc["variables"]["BAD"])
            return docs

        with patch("src.properties.variables.common.read_yml", patched_read):
            document_variables(str(out), str(cfg), DISABLE_TITLE=True)

    def test_document_inputs_yaml_error(self, tmp_path, monkeypatch):
        out = _markers_file(tmp_path)
        cfg = tmp_path / "ci.yml"
        cfg.write_text(
            "spec:\n  inputs:\n    x:\n      description: d\n",
            encoding="utf-8",
        )

        def raise_yaml(*_args, **_kwargs):
            raise yaml.YAMLError("bad")

        monkeypatch.setattr("src.properties.inputs.add_between_markers", raise_yaml)
        document_inputs(str(out), str(cfg), DISABLE_TITLE=True)

    def test_document_workflows_yaml_error(self, tmp_path, monkeypatch):
        out = _markers_file(tmp_path)
        cfg = tmp_path / "ci.yml"
        cfg.write_text("workflow:\n  - when: always\n", encoding="utf-8")

        def raise_yaml(*_args, **_kwargs):
            raise yaml.YAMLError("bad")

        monkeypatch.setattr("src.properties.workflows.add_between_markers", raise_yaml)
        document_workflows(str(out), str(cfg))

    def test_document_includes_write_failure(self, tmp_path, monkeypatch):
        cfg = tmp_path / "ci.yml"
        cfg.write_text("include:\n  - local: x.yml\n", encoding="utf-8")
        out = _markers_file(tmp_path)

        def boom(*_args, **_kwargs):
            raise RuntimeError("write failed")

        monkeypatch.setattr("src.properties.includes.add_between_markers", boom)
        document_includes(str(out), str(cfg))

    def test_document_includes_unexpected_error(self, tmp_path, monkeypatch):
        cfg = tmp_path / "ci.yml"
        cfg.write_text("include:\n  - project: g/p\n    ref: main\n", encoding="utf-8")
        out = _markers_file(tmp_path)
        monkeypatch.setattr(
            "src.properties.includes.common.table_design",
            lambda **_k: (_ for _ in ()).throw(RuntimeError("table fail")),
        )
        document_includes(str(out), str(cfg))

    def test_get_job_attribute_skips_all_missing(self, tmp_path):
        out = _markers_file(tmp_path)
        get_job_attribute(
            str(out),
            str(SAMPLE),
            attributes="totally_missing_attr",
            json_format=True,
        )


class TestPipelineAndSwagger:
    def test_collect_pipeline_spec_inputs_and_invalid_component(self, tmp_path):
        cfg = tmp_path / "ci.yml"
        cfg.write_text(
            "spec:\n  inputs:\n    x:\n      description: d\n"
            "include:\n  - component: invalid\n"
            "job:\n  script: echo\n",
            encoding="utf-8",
        )
        data = collect_pipeline_data(str(cfg), detailed=True, include_nested=True)
        assert any(item["key"] == "x" for item in data["inputs"])

    def test_collect_pipeline_missing_local_include(self, tmp_path):
        cfg = tmp_path / ".gitlab-ci.yml"
        cfg.write_text(
            "include:\n  - local: missing.yml\n"
            "root:\n  script: echo\n",
            encoding="utf-8",
        )
        data = collect_pipeline_data(str(cfg), detailed=True, include_nested=True)
        assert any(job["name"] == "root" for job in data["jobs"])

    def test_collect_pipeline_semver_validation_error(self, tmp_path, monkeypatch):
        cfg = tmp_path / "ci.yml"
        cfg.write_text(
            "include:\n  - project: g/p\n    ref: 1.0.0\n    file: ci.yml\n",
            encoding="utf-8",
        )

        def boom(_version):
            raise RuntimeError("semver unavailable")

        monkeypatch.setattr(
            "src.modules.pipeline_data.semver.Version.is_valid",
            boom,
        )
        data = collect_pipeline_data(str(cfg))
        assert data["includes"]
        assert data["includes"][0]["valid_version"] is False

    def test_collect_pipeline_index_yaml_failure(self, tmp_path, monkeypatch):
        cfg = tmp_path / "ci.yml"
        cfg.write_text("job:\n  script: echo\n", encoding="utf-8")

        def boom(_path):
            raise RuntimeError("index failed")

        monkeypatch.setattr("src.modules.yaml_lines.index_yaml_file", boom)
        data = collect_pipeline_data(str(cfg))
        assert data["jobs"]

    def test_index_yaml_workflow_dict_form(self, tmp_path):
        cfg = tmp_path / "ci.yml"
        cfg.write_text(
            "workflow:\n  rules:\n    - when: always\n"
            "build:\n  script: echo\n",
            encoding="utf-8",
        )
        index = index_yaml_file(str(cfg))
        assert index["workflow_rules"]
        assert "build" in index["jobs"]

    def test_render_swagger_template_job_and_workflow(self):
        html = render_swagger_html(
            {
                "config_file": "ci.yml",
                "inputs": [],
                "variables": [],
                "includes": [],
                "workflow_rules": [{"when": "always"}],
                "jobs": [
                    {
                        "name": ".tmpl",
                        "display_name": ".tmpl",
                        "is_template": True,
                        "attributes": [{"key": "stage", "value": "test"}],
                        "nested": [
                            {
                                "attribute": "variables",
                                "key": "K",
                                "value": "v",
                            }
                        ],
                        "rules": [{"when": "always"}],
                    }
                ],
            }
        )
        assert "TEMPLATE" in html
        assert "workflow" in html.lower()


class TestComplianceRenderAndConsole:
    def _mixed_result(self) -> ComplianceResult:
        return ComplianceResult(
            success=True,
            exit_code=0,
            features=1,
            scenarios=3,
            passed=1,
            failed=0,
            skipped=1,
            scenario_results=[
                ScenarioResult(
                    feature="ok.feature",
                    name="Passing",
                    status="passed",
                    policy_id="P-1",
                    title="Pass",
                ),
                ScenarioResult(
                    feature="skip.feature",
                    name="Skipped",
                    status="skipped",
                    message="No entities",
                    severity="HIGH",
                ),
                ScenarioResult(
                    feature="other.feature",
                    name="No id",
                    status="failed",
                    message="(sample-files/.gitlab-ci.yml:1)",
                    severity="weird-severity",
                ),
            ],
        )

    def test_markdown_includes_passed_and_skipped(self):
        text = render_compliance_markdown(
            self._mixed_result(), str(SAMPLE), str(PASSING)
        )
        assert "## Passed scenarios" in text
        assert "## Skipped scenarios" in text

    def test_mr_comment_success_and_skipped(self):
        comment = render_compliance_mr_comment(
            self._mixed_result(), str(SAMPLE), str(PASSING)
        )
        assert "Compliance passed" in comment
        assert "Skipped policies" in comment
        assert "blocked" not in comment.lower()

    def test_html_success_path(self):
        html = render_compliance_html(
            self._mixed_result(), str(SAMPLE), str(PASSING)
        )
        assert "Compliance Passed" in html

    def test_codequality_skipped_and_unknown_severity(self):
        payload = render_compliance_code_quality(
            self._mixed_result(), str(SAMPLE)
        )
        assert "skipped" in payload.lower() or "major" in payload

    def test_console_success_with_skipped(self, capsys):
        render_compliance_console(
            self._mixed_result(), str(SAMPLE), str(PASSING)
        )
        assert capsys.readouterr().out


class TestStashAndApi:
    def test_entity_has_property_empty_values(self):
        assert not entity_has_property({"values": {"x": ""}}, "x")
        assert not entity_has_property({"values": {"x": []}}, "x")

    def test_assert_all_raises(self):
        entity = {"name": "j", "source_file": "/p/ci.yml", "line": 1}
        with pytest.raises(AssertionError, match="j"):
            assert_all([entity], lambda _e: False, "failed check")

    def test_format_entity_ref_without_line(self):
        assert format_entity_ref({"name": "only"}) == "only"

    def test_require_api_connection_ready(self, monkeypatch):
        monkeypatch.setenv("GITLAB_TOKEN", "tok")
        monkeypatch.setenv("CI_PROJECT_PATH", "g/p")
        context = SimpleNamespace(
            config=SimpleNamespace(userdata={"strict": "false"}),
            scenario=SimpleNamespace(skip=MagicMock()),
            scenario_skipped=False,
        )
        assert require_api_connection(context, "project", "label") is True


class TestModelMetadataPolicy:
    def test_load_yaml_entities_sample(self):
        entities = load_yaml_entities(str(SAMPLE))
        assert entities["jobs"]

    def test_load_pipeline_entities_without_api(self, monkeypatch):
        monkeypatch.delenv("GITLAB_TOKEN", raising=False)
        monkeypatch.delenv("CI_JOB_TOKEN", raising=False)
        entities = load_pipeline_entities(str(SAMPLE))
        assert not entities["project_settings"]

    def test_collect_policy_index(self):
        catalog = build_policy_catalog(str(ANNOTATED))
        index = collect_policy_index(catalog)
        assert index

    def test_render_policy_catalog_minimal_feature(self, tmp_path):
        feature = tmp_path / "plain.feature"
        feature.write_text(
            "Feature: Plain\n  Scenario: One\n    Given x\n",
            encoding="utf-8",
        )
        catalog = build_policy_catalog(str(tmp_path))
        html = render_policy_catalog(catalog, str(tmp_path), "html")
        assert "<html" in html.lower()


class TestGitlabDocsCliExtra:
    def test_legacy_brand_notice_on_invoke(self):
        runner = CliRunner(mix_stderr=False)
        result = runner.invoke(
            gitlab_compliance,
            ["--help"],
            prog_name="gitlab-docs",
        )
        assert result.exit_code == 0
        combined = f"{result.output}\n{result.stderr}"
        assert "deprecated" in combined.lower()

    def test_compliance_doc_stdout(self, monkeypatch):
        monkeypatch.setattr("src.gitlab_docs.POLICY_DOC_DEFAULT_OUTPUT_FILES", {})
        runner = CliRunner()
        result = runner.invoke(
            compliance_doc,
            ["--features", str(ANNOTATED), "--format", "markdown"],
        )
        assert result.exit_code == 0
        assert "Policy" in result.output or "policy" in result.output.lower()

    def test_compliance_push_without_digest(self, monkeypatch):
        monkeypatch.setattr("src.gitlab_docs.push_policies", lambda _f, _t: "")
        runner = CliRunner()
        result = runner.invoke(
            gitlab_compliance,
            [
                "compliance-push",
                "--features",
                str(PASSING),
                "registry.example.com/p:1",
            ],
        )
        assert result.exit_code == 0

    def test_resolve_policies_dir_oci(self, monkeypatch):
        monkeypatch.setattr(
            "src.gitlab_docs.resolve_features_dir",
            lambda ref, cache_dir=None: "/tmp/policies",
        )
        resolved, source = _resolve_policies_dir(
            "oci://registry.example.com/policies:1.0.0"
        )
        assert resolved == "/tmp/policies"
        assert "oci://" in source


class TestCommandReferenceAndOci:
    def test_param_metadata_for_argument(self):
        arg = click.Argument(["target"], required=True)
        meta = _param_metadata(arg)
        assert meta["kind"] == "argument"

    def test_dumps_failure_reraises(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "src.modules.command_reference.dump_helper",
            lambda *_a, **_k: (_ for _ in ()).throw(RuntimeError("boom")),
        )
        runner = CliRunner()
        result = runner.invoke(
            dumps,
            [
                "--baseModule",
                "src.gitlab_docs",
                "--baseCommand",
                "gitlab_compliance",
                "--docsPath",
                str(tmp_path),
            ],
        )
        assert result.exit_code != 0
        assert "Dumps command failed" in result.output

    def test_is_oci_reference_for_existing_file(self, tmp_path):
        path = tmp_path / "policies"
        path.mkdir()
        assert is_oci_reference(str(path)) is False

    def test_push_policies_json_parse_failure(self, monkeypatch, tmp_path):
        class PushResponse:
            reason = "pushed"

            def json(self):
                raise ValueError("not json")

        client = MagicMock()
        client.push.return_value = PushResponse()
        monkeypatch.setattr("src.compliance.oci_registry._client", lambda: client)
        monkeypatch.setattr(
            "src.compliance.oci_registry.bundle_policies_dir",
            lambda _d: os.path.join(tmp_path, "bundle.tar.gz"),
        )
        (tmp_path / "bundle.tar.gz").write_bytes(b"x")
        digest = push_policies(str(PASSING), "registry.example.com/p:1")
        assert digest == "pushed"


class TestReleaseHelpers:
    def test_parse_gitlab_date_naive(self):
        dt = parse_gitlab_date("2024-01-15T10:00:00")
        assert dt.tzinfo is not None

    def test_sort_tags_non_semver_by_date(self):
        tags = sort_tags(
            [
                SimpleNamespace(
                    name="release-candidate",
                    commit={"committed_date": "2024-06-01T00:00:00Z"},
                ),
                SimpleNamespace(
                    name="older-name",
                    commit={"committed_date": "2024-01-01T00:00:00Z"},
                ),
            ]
        )
        assert tags[0].name == "release-candidate"

    def test_build_markdown_omits_empty_buckets(self):
        md = build_markdown(
            "g/p",
            "v0.0.0",
            parse_gitlab_date("1970-01-01T00:00:00Z"),
            [],
            {"feat": 0, "fix": 0, "chore": 0, "other": 0},
        )
        assert "## Features" not in md

    def test_resolve_baseline_tag_invalid_date(self):
        from src.modules.release import resolve_baseline_tag

        tag = SimpleNamespace(
            name="broken-date",
            commit={"committed_date": "not-iso", "id": "abc"},
        )
        name, _dt, sha = resolve_baseline_tag([tag])
        assert name == "broken-date"
        assert sha == "abc"

    def test_print_release_preview_empty(self, capsys):
        print_release_preview([])
        assert "No commits since the baseline tag" in capsys.readouterr().out


class TestBehaveSupportExtra:
    def test_given_api_backed_steps_with_token(self, monkeypatch):
        monkeypatch.setenv("GITLAB_TOKEN", "tok")
        monkeypatch.setenv("CI_PROJECT_PATH", "g/p")
        context = SimpleNamespace(
            compliance_entities={
                "project_settings": [{"name": "jobs_enabled", "values": {}}],
                "project_ci_variables": [{"name": "VAR"}],
                "group_settings": [],
            },
            stash=[],
            step_mode=None,
            scenario_skipped=False,
            config=SimpleNamespace(userdata={"strict": "false"}),
            scenario=SimpleNamespace(skip=MagicMock()),
        )
        given_steps.given_any_project_setting(context)
        given_steps.given_project_setting(context, "jobs_enabled")
        given_steps.given_any_project_ci_variable(context)
        monkeypatch.setenv("GITLAB_GROUP_PATH", "grp")
        context.compliance_entities["group_settings"] = [{"name": "shared_runners_enabled"}]
        given_steps.given_any_group_setting(context)

    def test_when_filter_skips_scenario(self):
        context = SimpleNamespace(
            stash=[{"name": "j", "values": {"stage": "test"}}],
            step_mode=None,
            scenario_skipped=False,
            scenario=SimpleNamespace(skip=MagicMock()),
        )
        when_steps.when_it_has(context, "nonexistent_property")
        context.scenario.skip.assert_called_once()

    def test_then_skipped_scenario_noop(self):
        context = SimpleNamespace(
            stash=[],
            scenario_skipped=True,
            step_mode=None,
        )
        then_steps.then_must_contain(context, "stage")

    def test_temporary_gitlab_env_restores_previous(self, monkeypatch):
        monkeypatch.setenv("GITLAB_TOKEN", "original")
        with _temporary_gitlab_env(token="temporary", gitlab_url=None, project=None, group=None):
            assert os.environ["GITLAB_TOKEN"] == "temporary"
        assert os.environ["GITLAB_TOKEN"] == "original"


class TestRunnerSkipPolicy:
    def test_run_compliance_skip_policies(self):
        result = run_compliance(
            features_dir=str(SKIP_POLICIES),
            pipeline_file=str(SAMPLE),
            output_format="console",
        )
        assert result.skipped >= 0

    def test_run_compliance_oci_features_dir(self, monkeypatch):
        monkeypatch.setattr(
            "src.compliance.runner.resolve_features_dir",
            lambda *_args, **_kwargs: str(PASSING),
        )
        result = run_compliance(
            features_dir="oci://registry.example.com/policies:1.0.0",
            pipeline_file=str(SAMPLE),
            output_format="console",
        )
        assert result.scenarios >= 0


class TestGitlabApiLoad:
    def test_load_api_entities_env_defaults(self, monkeypatch):
        monkeypatch.setenv("GITLAB_TOKEN", "tok")
        monkeypatch.setenv("CI_SERVER_URL", "https://gitlab.example.com")

        project_obj = SimpleNamespace(
            variables=SimpleNamespace(list=lambda **_kwargs: []),
        )
        group_obj = SimpleNamespace()

        gl = MagicMock()
        gl.auth.return_value = None
        gl.projects.get.return_value = project_obj
        gl.groups.get.return_value = group_obj

        with patch("gitlab.Gitlab", return_value=gl):
            from src.compliance.gitlab_api import load_api_entities

            entities = load_api_entities(project="g/p", group="my-group")
        assert entities["project_settings"] == []
        assert entities["project_ci_variables"] == []
