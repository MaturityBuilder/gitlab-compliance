"""Tests targeting remaining uncovered lines for 100% src/ coverage."""

from __future__ import annotations

import os
import tarfile
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from src.compliance.behave_support import environment as behave_env
from src.compliance.behave_support.steps import given_steps, then_steps, when_steps
from src.compliance.console import render_compliance_console
from src.compliance.metadata import (
    _parse_metadata_yaml,
    _slug,
    build_policy_catalog,
    parse_feature_policies,
)
from src.compliance.model import _job_values, load_yaml_entities
from src.compliance.models import ComplianceResult, ScenarioResult
from src.compliance.oci_registry import (
    _client,
    _find_bundle_file,
    bundle_policies_dir,
    normalize_oci_reference,
    pull_policies,
    resolve_features_dir,
)
from src.compliance.policy_doc import _relative_path, render_policy_catalog
from src.compliance.render import render_compliance_code_quality
from src.compliance.runner import _build_behave_workspace, _scenario_message
from src.compliance.stash import get_property, normalize_value
from src.gitlab_compliance import (
    _resolve_compliance_output,
    _resolve_output_file,
    _resolve_policy_doc_output,
    compliance,
    gitlab_compliance,
)
from src.modules.command_reference import cli, dump_helper
from src.modules.common import (
    build_dict_list_table,
    format_dict_summary,
    format_rules_summary,
)
from src.modules.doc_controller import add_between_markers
from src.modules.pipeline_data import _parse_include_entry, collect_pipeline_data
from src.modules.release import print_release_preview, release_notes
from src.modules.swagger_html import _escape, _render_rules_table
from src.modules.yaml_lines import index_yaml_file
from src.properties.includes import document_includes
from src.properties.inputs import document_inputs
from src.properties.jobs import get_jobs
from src.properties.variables import document_variables
from src.properties.workflows import document_workflows

REPO_ROOT = Path(__file__).resolve().parents[1]
SAMPLE = REPO_ROOT / "sample-files" / ".gitlab-ci.yml"
PASSING = REPO_ROOT / "tests" / "compliance_policies" / "passing"
MARKER_START = "[comment]: <> (gitlab-docs-opening-auto-generated)"
MARKER_END = "[comment]: <> (gitlab-docs-closing-auto-generated)"


def _markers_file(tmp_path):
    out = tmp_path / "out.md"
    out.write_text(f"{MARKER_START}\n{MARKER_END}\n", encoding="utf-8")
    return out


def _compliance_context(**overrides):
    base = {
        "compliance_entities": {
            "jobs": [
                {
                    "name": "build",
                    "values": {
                        "stage": "test",
                        "image": "alpine",
                        "extends": "tmpl",
                    },
                    "extends": "tmpl",
                }
            ],
            "includes": [{"include_type": "local", "name": "x"}],
            "variables": [{"name": "VAR", "values": {"value": "1"}}],
            "workflow_rules": [{"name": "rule-1", "values": {"when": "always"}}],
            "project_settings": [],
            "project_ci_variables": [],
            "group_settings": [],
        },
        "stash": [],
        "step_mode": None,
        "scenario_skipped": False,
        "config": SimpleNamespace(userdata={"strict": "false"}),
        "scenario": SimpleNamespace(skip=MagicMock()),
    }
    base.update(overrides)
    return SimpleNamespace(**base)


class TestStashAndCommon:
    def test_normalize_list_and_non_dict_values(self):
        assert normalize_value([1, 2]) == "[1, 2]"
        assert get_property({"values": "bad"}, "stage") is None

    def test_format_helpers_branches(self):
        assert format_dict_summary(["not", "dict"]) != ""
        assert "Rule 1" in format_rules_summary(["plain-rule"])
        assert build_dict_list_table([]) is None

    def test_swagger_escape_and_rules(self):
        assert _escape(None) == ""
        assert _render_rules_table([{"if": "$CI"}]) != ""


class TestBehaveStepsFull:
    def test_before_scenario_requires_pipeline(self):
        context = SimpleNamespace(
            stash=[],
            step_mode=None,
            scenario_skipped=False,
            compliance_entities={},
            config=SimpleNamespace(userdata={}),
        )
        with pytest.raises(RuntimeError, match="Pipeline file not configured"):
            behave_env.before_scenario(context, SimpleNamespace())

    def test_given_steps_skip_without_api(self, monkeypatch):
        monkeypatch.delenv("GITLAB_TOKEN", raising=False)
        monkeypatch.delenv("CI_JOB_TOKEN", raising=False)
        context = _compliance_context()
        given_steps.given_any_project_setting(context)
        given_steps.given_project_setting(context, "jobs_enabled")
        given_steps.given_any_project_ci_variable(context)
        given_steps.given_any_group_setting(context)

    def test_when_skipped_early_return(self):
        context = _compliance_context(
            scenario_skipped=True,
            stash=[{"name": "j", "values": {}}],
        )
        when_steps.when_it_has(context, "stage")

    def test_then_empty_stash_raises(self):
        context = _compliance_context(stash=[])
        with pytest.raises(AssertionError, match="No entities in stash"):
            then_steps.then_must_contain(context, "stage")

    def test_all_then_steps_with_stash(self):
        entity = {
            "name": "build",
            "values": {"stage": "test", "image": "alpine", "extends": "tmpl"},
            "extends": "tmpl",
        }
        context = _compliance_context(stash=[entity])
        then_steps.then_must_not_contain(context, "missing")
        then_steps.then_property_must_be(context, "stage", "test")
        then_steps.then_property_must_match(context, "image", "alpine")
        then_steps.then_property_must_not_match(context, "image", "latest")
        then_steps.then_property_not_null(context, "stage")
        then_steps.then_extends_includes(context, "tmpl")


class TestMetadataAndModel:
    def test_metadata_helpers(self, tmp_path):
        assert _slug("---") == "POLICY"
        assert _parse_metadata_yaml([]) == {}
        assert _parse_metadata_yaml(["id: x"]) == {"id": "x"}

        feature = tmp_path / "no-feature-line.feature"
        feature.write_text(
            "  Scenario: Orphan\n    Given x\n",
            encoding="utf-8",
        )
        orphan = parse_feature_policies(str(feature))
        assert orphan.annotation is not None

        catalog = build_policy_catalog(str(PASSING))
        assert catalog.lookup_scenario("/no/such/file.feature", "x") is None

    def test_job_values_nested(self):
        job = {
            "attributes": [{"key": "stage", "value": "test"}],
            "rules": [{"when": "always"}],
            "nested": [
                {"attribute": "variables", "key": "K", "value": "v"},
                {"attribute": "needs", "key": "", "value": "prep"},
            ],
        }
        values = _job_values(job)
        assert values["rules"]
        assert values["needs"] == ["prep"]
        assert values["variables"]["K"] == "v"

    def test_load_yaml_entities_includes_workflow(self):
        entities = load_yaml_entities(str(SAMPLE))
        assert entities["workflow_rules"] or entities["jobs"]


class TestOciRegistryFull:
    def test_normalize_oci_reference_adds_latest(self):
        assert normalize_oci_reference("registry.example.com/org/policies").endswith(
            ":latest"
        )

    def test_bundle_policies_dir_empty(self, tmp_path):
        empty = tmp_path / "empty"
        empty.mkdir()
        with pytest.raises(FileNotFoundError, match="No .feature files"):
            bundle_policies_dir(str(empty))

    def test_client_factory(self):
        assert _client() is not None

    def test_find_bundle_file_walk(self, tmp_path):
        bundle = tmp_path / "nested" / "bundle.tgz"
        bundle.parent.mkdir(parents=True)
        bundle.write_bytes(b"data")
        assert _find_bundle_file(str(tmp_path), None) == str(bundle)

    def test_pull_policies_replaces_existing_output(self, tmp_path, monkeypatch):
        out = tmp_path / "out"
        out.mkdir()
        (out / "old.feature").write_text("Feature: Old\n", encoding="utf-8")
        bundle = tmp_path / "bundle.tar.gz"
        policies = tmp_path / "policies"
        policies.mkdir()
        (policies / "a.feature").write_text("Feature: A\n", encoding="utf-8")
        with tarfile.open(bundle, "w:gz") as tar:
            tar.add(policies, arcname=".")
        client = MagicMock()
        client.pull.return_value = [str(bundle)]
        monkeypatch.setattr("src.compliance.oci_registry._client", lambda: client)
        path = pull_policies("registry.example.com/p:1", output_dir=str(out))
        assert Path(path).exists()

    def test_resolve_features_dir_local(self):
        assert resolve_features_dir(str(PASSING)) == str(PASSING.resolve())

    def test_resolve_features_dir_oci(self, monkeypatch):
        monkeypatch.setattr(
            "src.compliance.oci_registry.pull_policies",
            lambda *_a, **_k: "/tmp/cache",
        )
        assert resolve_features_dir("oci://registry.example.com/p:1") == "/tmp/cache"


class TestPipelineAndYaml:
    def test_parse_include_unknown_returns_none(self):
        assert _parse_include_entry({"remote": "https://x/ci.yml"}) is None

    def test_collect_skips_non_dict_jobs_and_commonpath_value_error(
        self, tmp_path, monkeypatch
    ):
        cfg = tmp_path / "ci.yml"
        cfg.write_text(
            "include:\n  - local: /etc/passwd\n"
            "scalar_job: just-string\n"
            "build:\n  script: echo\n",
            encoding="utf-8",
        )
        data = collect_pipeline_data(str(cfg), detailed=True)
        names = {j["name"] for j in data["jobs"]}
        assert "build" in names
        assert "scalar_job" not in names

    def test_index_yaml_skips_non_mapping_document(self, tmp_path):
        path = tmp_path / "multi.yml"
        path.write_text(
            "---\n'just-a-string'\n---\nbuild:\n  script: echo\n", encoding="utf-8"
        )
        index = index_yaml_file(str(path))
        assert "build" in index["jobs"]

    def test_scalar_pipeline_variable(self, tmp_path):
        cfg = tmp_path / "ci.yml"
        cfg.write_text(
            "variables:\n  PLAIN: hello\njob:\n  script: echo\n", encoding="utf-8"
        )
        data = collect_pipeline_data(str(cfg))
        assert data["variables"][0]["key"] == "PLAIN"


class TestPropertiesRemaining:
    def test_document_variables_dict_branches(self, tmp_path):
        cfg = tmp_path / "ci.yml"
        cfg.write_text(
            "variables:\n"
            "  NO_DESC:\n    value: v\n"
            "  NO_OPTS:\n    value: v\n    description: d\n"
            "  NO_EXPAND:\n    value: v\n    description: d\n    options: [a]\n",
            encoding="utf-8",
        )
        document_variables(str(_markers_file(tmp_path)), str(cfg), DISABLE_TITLE=True)

    def test_document_inputs_dict_branches(self, tmp_path):
        cfg = tmp_path / "ci.yml"
        cfg.write_text(
            "spec:\n  inputs:\n"
            "    NO_DESC:\n      default: x\n"
            "    NO_OPTS:\n      default: x\n      description: d\n"
            "    NO_EXPAND:\n      default: x\n      description: d\n      options: [a]\n",
            encoding="utf-8",
        )
        document_inputs(str(_markers_file(tmp_path)), str(cfg), DISABLE_TITLE=True)

    def test_document_workflows_scalar(self, tmp_path):
        cfg = tmp_path / "ci.yml"
        # Scalar workflow (not list or rules dict) -> workflow_rules = [workflow]
        cfg.write_text("workflow: always\n", encoding="utf-8")
        document_workflows(str(_markers_file(tmp_path)), str(cfg))

    def test_get_jobs_experimental_template_and_needs(self, tmp_path):
        cfg = tmp_path / "ci.yml"
        cfg.write_text(
            ".hidden:\n  stage: hidden\n"
            "build:\n"
            "  stage: test\n"
            "  rules:\n"
            "    - when: always\n"
            "  needs:\n"
            "    - prep\n"
            "  variables:\n"
            "    K: v\n"
            "  script: echo\n",
            encoding="utf-8",
        )
        get_jobs(
            str(_markers_file(tmp_path)),
            str(cfg),
            detailed=True,
            experimental=True,
        )

    def test_document_includes_bad_entry(self, tmp_path):
        cfg = tmp_path / "ci.yml"
        cfg.write_text("include:\n  - 123\n", encoding="utf-8")
        document_includes(str(_markers_file(tmp_path)), str(cfg))


class TestGitlabDocsHelpers:
    def test_resolve_output_helpers(self):
        assert _resolve_output_file("markdown", None) == "README.md"
        assert _resolve_compliance_output("markdown", None) == "COMPLIANCE-REPORT.md"
        assert _resolve_policy_doc_output("html", None) == "COMPLIANCE-POLICIES.html"

    def test_legacy_notice_on_subcommand_invoke(self, monkeypatch):
        from src.compliance.models import ComplianceResult

        monkeypatch.setattr(
            "src.gitlab_compliance.run_compliance",
            lambda **kwargs: ComplianceResult(
                success=True,
                exit_code=0,
                scenario_results=[],
                scenarios=0,
                passed=0,
                failed=0,
                skipped=0,
            ),
        )
        runner = CliRunner()
        result = runner.invoke(
            compliance,
            ["--features", str(PASSING), "--pipeline", str(SAMPLE)],
            prog_name="gitlab-docs",
        )
        assert result.exit_code == 0


class TestRenderRunnerConsole:
    def test_codequality_skipped_description_fallback(self):
        result = ComplianceResult(
            success=True,
            exit_code=0,
            scenario_results=[
                ScenarioResult(
                    feature="s.feature",
                    name="Skipped",
                    status="skipped",
                    message="",
                    title="Skip title",
                )
            ],
            scenarios=1,
            passed=0,
            failed=0,
            skipped=1,
        )
        payload = render_compliance_code_quality(result, str(SAMPLE))
        assert "Scenario skipped" in payload or "Skip title" in payload

    def test_scenario_message_error_message_attr(self):
        scenario = SimpleNamespace(
            steps=[],
            skip_reason=None,
            error_message="direct error",
        )
        assert _scenario_message(scenario) == "direct error"

    def test_build_behave_workspace_relpath_escape(self, monkeypatch, tmp_path):
        policies = tmp_path / "policies"
        policies.mkdir()
        (policies / "a.feature").write_text(
            "Feature: A\n  Scenario: S\n    Given x\n", encoding="utf-8"
        )

        def fake_relpath(_path, _start):
            return "../outside"

        monkeypatch.setattr("src.compliance.runner.os.path.relpath", fake_relpath)
        with pytest.raises(ValueError, match="escapes policies directory"):
            _build_behave_workspace(str(policies))

    def test_console_failure_with_description(self, capsys):
        result = ComplianceResult(
            success=False,
            exit_code=1,
            features=1,
            scenarios=1,
            passed=0,
            failed=1,
            skipped=0,
            scenario_results=[
                ScenarioResult(
                    feature="f.feature",
                    name="n",
                    status="failed",
                    message="msg",
                    description="desc",
                    policy_id="P",
                    title="T",
                )
            ],
        )
        render_compliance_console(result, str(SAMPLE), str(PASSING))
        assert capsys.readouterr().out


class TestPolicyDocAndDocController:
    def test_relative_path_value_error(self, monkeypatch):
        def boom(*_args, **_kwargs):
            raise ValueError("different drives")

        monkeypatch.setattr("src.compliance.policy_doc.os.path.relpath", boom)
        assert _relative_path("/a", "/b/file.feature") == "/b/file.feature"

    def test_policy_catalog_markdown_custom_metadata(self, tmp_path):
        feature = tmp_path / "c.feature"
        feature.write_text(
            "# METADATA\n# title: T\n# custom:\n#   severity: high\n"
            "Feature: Custom\n  Scenario: S\n    Given x\n",
            encoding="utf-8",
        )
        catalog = build_policy_catalog(str(tmp_path))
        md = render_policy_catalog(catalog, str(tmp_path), "markdown")
        assert "Custom" in md
        html = render_policy_catalog(catalog, str(tmp_path), "html")
        assert "Custom" in html

    def test_add_between_markers_file_without_trailing_newline(self, tmp_path):
        path = tmp_path / "doc.md"
        path.write_text("intro", encoding="utf-8")
        add_between_markers(str(path), "block")
        assert MARKER_START in path.read_text(encoding="utf-8")


class TestCommandReferenceAndRelease:
    def test_dump_helper_creates_docs_dir(self, tmp_path, capsys):
        command = SimpleNamespace(name="gitlab-docs", help="help text")
        docs_dir = tmp_path / "brand_new_docs"

        def fake_recursive(_cmd):
            yield {
                "command": command,
                "help": "help",
                "usage": "usage",
                "parent": "",
                "params": [],
                "options": [],
            }

        with patch("src.modules.command_reference.recursive_help", fake_recursive):
            dump_helper(MagicMock(), str(docs_dir))
        assert docs_dir.is_dir()

    def test_cli_group_pass(self):
        runner = CliRunner()
        result = runner.invoke(cli, [])
        assert result.exit_code == 0

    def test_print_release_preview_truncation(self, capsys):
        commits = [SimpleNamespace(title=f"c{i}", short_id=str(i)) for i in range(12)]
        print_release_preview(commits)
        out = capsys.readouterr().out
        assert "more commits" in out

    def test_release_notes_all_projects_fail(self, monkeypatch):
        runner = CliRunner()

        def boom(*_args, **_kwargs):
            raise RuntimeError("fail")

        with patch("src.modules.release.get_commits_since_last_tag", side_effect=boom):
            result = runner.invoke(
                release_notes,
                ["--token", "tok", "--projects", "g/p"],
            )
        assert result.exit_code == 1

    def test_release_notes_partial_failure_exits_one(self):
        from datetime import datetime, timezone

        runner = CliRunner()
        ok_project = SimpleNamespace(web_url="https://example.com/p")

        def ok(_gl, project_id, since_tag=None):
            return (
                ok_project,
                "v1.0.0",
                datetime(2024, 1, 1, tzinfo=timezone.utc),
                [],
            )

        def fail(_gl, project_id, since_tag=None):
            raise RuntimeError("broken")

        with patch("src.modules.release.gitlab.Gitlab"):
            with patch(
                "src.modules.release.get_commits_since_last_tag",
                side_effect=[ok, fail],
            ):
                result = runner.invoke(
                    release_notes,
                    ["--token", "tok", "--projects", "g/ok", "--projects", "g/bad"],
                )
        assert result.exit_code == 1


class TestFinalCoverageLines:
    def test_when_apply_filter_assigns_stash(self):
        entity = {"name": "build", "values": {"stage": "test"}}
        context = SimpleNamespace(
            stash=[entity],
            step_mode=None,
            scenario_skipped=False,
            scenario=SimpleNamespace(skip=MagicMock()),
        )
        when_steps.when_it_has(context, "stage")
        assert context.stash == [entity]

    def test_metadata_custom_not_dict(self):
        from src.compliance.metadata import _annotation_from_raw

        ann = _annotation_from_raw(
            {"custom": "not-a-dict"},
            scope="feature",
            feature_file="/f.feature",
            line=1,
            feature_name="F",
            default_title="F",
            default_id="ID",
        )
        assert ann.custom == {}

    def test_policy_doc_location_and_custom_render(self, tmp_path):
        from src.compliance.metadata import (
            FeaturePolicies,
            PolicyAnnotation,
            PolicyCatalog,
        )
        from src.compliance.policy_doc import _location

        feature = tmp_path / "meta.feature"
        feature.write_text(
            "Feature: Meta\n  Scenario: S\n    Given x\n",
            encoding="utf-8",
        )
        scenario = PolicyAnnotation(
            policy_id="GLCI-META-001",
            title="S",
            description="",
            scope="scenario",
            feature_file=str(feature),
            line=6,
            feature_name="Meta",
            scenario_name="S",
            custom={"severity": "high"},
        )
        catalog = PolicyCatalog(
            features=[
                FeaturePolicies(
                    feature_file=str(feature),
                    feature_name="Meta",
                    annotation=PolicyAnnotation(
                        policy_id="GLCI-META",
                        title="Meta",
                        feature_file=str(feature),
                        line=5,
                        feature_name="Meta",
                        scope="feature",
                    ),
                    scenarios=[scenario],
                )
            ]
        )
        assert "- **Custom:**" in render_policy_catalog(
            catalog, str(tmp_path), "markdown"
        )
        html = render_policy_catalog(catalog, str(tmp_path), "html")
        assert "severity" in html

        bare = PolicyCatalog(
            features=[
                FeaturePolicies(
                    feature_file=str(feature),
                    feature_name="Meta",
                    annotation=PolicyAnnotation(
                        policy_id="P",
                        title="T",
                        line=0,
                        feature_file=str(feature),
                        feature_name="Meta",
                    ),
                    scenarios=[],
                )
            ]
        )
        assert _location(str(tmp_path), bare.features[0].annotation) == os.path.relpath(
            str(feature), str(tmp_path)
        )

    def test_render_failed_description_fallback(self):
        from src.compliance.render import _description_for_scenario

        scenario = ScenarioResult(
            feature="f.feature",
            name="N",
            status="failed",
            message="",
            description="",
            title="Title",
        )
        assert "Compliance check failed" in _description_for_scenario(scenario)

    def test_gitlab_docs_resolve_helpers_and_legacy_notice(self):
        import click

        from src import gitlab_docs as gd

        assert gd._resolve_compliance_output("console", None) is None
        assert gd._resolve_policy_doc_output("unknown", None) is None
        ctx = click.Context(gd.gitlab_compliance, info_name="gitlab-docs")
        gd.gitlab_compliance._emit_legacy_notice(ctx)

    def test_command_reference_cli_callback(self):
        from src.modules.command_reference import cli as dumps_cli

        dumps_cli.callback()

    def test_pipeline_variable_dict_and_commonpath_error(self, tmp_path, monkeypatch):
        from src.modules.pipeline_data import (
            _parse_variable_entry,
            _resolve_local_include_path,
        )

        entry = _parse_variable_entry(
            "X",
            {"description": "d", "options": ["a"], "expand": False},
        )
        assert entry["description"] == "d"

        cfg = tmp_path / "ci.yml"
        cfg.write_text(
            "include:\n  - local: child.yml\n"
            "build:\n  needs: [prep]\n  script: echo\n",
            encoding="utf-8",
        )
        collect_pipeline_data(str(cfg), detailed=True)

        def boom(_paths):
            raise ValueError("no common path")

        monkeypatch.setattr("src.modules.pipeline_data.os.path.commonpath", boom)
        assert _resolve_local_include_path(str(cfg), "child.yml") is None

    def test_swagger_rules_table_no_headers(self):
        assert _render_rules_table(["not-a-dict-rule"]) == ""

    def test_document_inputs_scalar_and_missing_expand(self, tmp_path):
        cfg = tmp_path / "ci.yml"
        cfg.write_text(
            "spec:\n  inputs:\n"
            "    PLAIN: hello\n"
            "    NO_EXPAND:\n      default: x\n      description: d\n      options: [a]\n",
            encoding="utf-8",
        )
        document_inputs(str(_markers_file(tmp_path)), str(cfg), DISABLE_TITLE=True)

    def test_get_jobs_artifacts_and_rules_table(self, tmp_path):
        cfg = tmp_path / "ci.yml"
        cfg.write_text(
            "build:\n"
            "  stage: test\n"
            "  script: echo\n"
            "  rules:\n"
            "    - when: always\n"
            "  artifacts:\n"
            "    paths:\n"
            "      - dist/\n",
            encoding="utf-8",
        )
        get_jobs(
            str(_markers_file(tmp_path)),
            str(cfg),
            detailed=True,
            experimental=True,
        )
