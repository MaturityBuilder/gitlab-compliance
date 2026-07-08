import os
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from click.testing import CliRunner

from src.compliance.behave_support import environment as behave_env
from src.compliance.behave_support.steps import given_steps, then_steps, when_steps
from src.compliance.oci_registry import (
    pull_policies,
    push_policies,
    resolve_features_dir,
)
from src.compliance.render import _status_icon, render_compliance_report
from src.compliance.runner import _assert_within_directory, _temporary_gitlab_env
from src.gitlab_compliance import check, generate_html
from src.modules.command_reference import dumps
from src.modules.logging import configure_logger
from src.modules.pipeline_data import collect_pipeline_data
from src.modules.release import filter_commits_since_tag, sort_tags
from src.modules.swagger_html import render_swagger_html
from src.modules.yaml_lines import index_yaml_file
from src.modules.yaml_md_table import generate_markdown_table

REPO_ROOT = Path(__file__).resolve().parents[1]
SAMPLE = REPO_ROOT / "examples/sample-files" / ".gitlab-ci.yml"
PASSING = REPO_ROOT / "tests" / "compliance_policies" / "passing"


class TestGitlabDocsBranches:
    def test_generate_html_without_click_context(self, tmp_path, monkeypatch):
        out = tmp_path / "out.html"
        monkeypatch.setattr("click.get_current_context", lambda silent=True: None)
        runner = CliRunner()
        result = runner.invoke(
            generate_html,
            ["--input-config", str(SAMPLE), "--output-file", str(out)],
        )
        assert result.exit_code == 0, result.output
        assert out.is_file()

    def test_compliance_echo_report_when_no_output_target(self, monkeypatch):
        from src import gitlab_docs as gd
        from src.compliance.models import ComplianceResult

        result = ComplianceResult(
            success=True,
            exit_code=0,
            scenario_results=[],
            scenarios=0,
            passed=0,
            failed=0,
            skipped=0,
        )
        monkeypatch.setattr(gd, "run_compliance", lambda **kwargs: result)
        monkeypatch.setattr(gd, "render_compliance_report", lambda **kwargs: "# report")
        monkeypatch.setattr(
            "src.gitlab_compliance._resolve_compliance_output",
            lambda fmt, out: None,
        )

        runner = CliRunner()
        invoke_result = runner.invoke(
            check,
            [
                "--features",
                str(PASSING),
                "--pipeline",
                str(SAMPLE),
                "--format",
                "markdown",
            ],
        )
        assert invoke_result.exit_code == 0, invoke_result.output
        assert "# report" in invoke_result.output


class TestCommandReferenceErrors:
    def test_dumps_missing_command(self, tmp_path):
        runner = CliRunner()
        result = runner.invoke(
            dumps,
            [
                "--baseModule",
                "src.gitlab_compliance",
                "--baseCommand",
                "not_a_command",
                "--docsPath",
                str(tmp_path),
            ],
        )
        assert result.exit_code == 0
        assert "Could not find command" in result.output


class TestPipelineAndYaml:
    def test_collect_pipeline_data_missing_file(self):
        with pytest.raises(FileNotFoundError):
            collect_pipeline_data("/no/ci.yml")

    def test_collect_pipeline_data_no_nested(self):
        data = collect_pipeline_data(str(SAMPLE), include_nested=False)
        assert "jobs" in data

    def test_index_yaml_file(self):
        index = index_yaml_file(str(SAMPLE))
        assert isinstance(index, dict)

    def test_generate_markdown_table(self):
        assert "a" in generate_markdown_table([{"a": "1", "b": "2"}])


class TestSwaggerHtml:
    def test_render_empty_pipeline(self):
        html = render_swagger_html(
            {
                "config_file": ".gitlab-ci.yml",
                "jobs": [],
                "includes": [],
                "variables": [],
                "inputs": [],
                "workflow_rules": [],
            }
        )
        assert "html" in html.lower()


class TestOciPushPull:
    def test_push_policies_mock(self, monkeypatch):
        response = MagicMock()
        response.json.return_value = {"digest": "sha256:abc"}
        client = MagicMock()
        client.push.return_value = response
        monkeypatch.setattr("src.compliance.oci_registry._client", lambda: client)
        monkeypatch.setattr(
            "src.compliance.oci_registry.bundle_policies_dir",
            lambda _d: os.path.join(tempfile.mkdtemp(), "b.tar.gz"),
        )
        digest = push_policies(str(PASSING), "registry.example.com/p:1")
        assert digest == "sha256:abc"

    def test_push_policies_reason_fallback(self, monkeypatch):
        response = MagicMock(spec=[])
        response.reason = "Created"
        client = MagicMock()
        client.push.return_value = response
        monkeypatch.setattr("src.compliance.oci_registry._client", lambda: client)
        monkeypatch.setattr(
            "src.compliance.oci_registry.bundle_policies_dir",
            lambda _d: os.path.join(tempfile.mkdtemp(), "b.tar.gz"),
        )
        assert push_policies(str(PASSING), "registry.example.com/p:1") == "Created"

    def test_pull_policies_missing_bundle_raises(self, monkeypatch):
        client = MagicMock()
        client.pull.return_value = []
        monkeypatch.setattr("src.compliance.oci_registry._client", lambda: client)
        with pytest.raises(FileNotFoundError):
            pull_policies(
                "registry.example.com/p:1",
                output_dir=os.fspath(Path(tempfile.mkdtemp())),
            )

    def test_pull_policies_mock(self, tmp_path, monkeypatch):
        bundle = tmp_path / "bundle.tar.gz"
        import tarfile

        policies = tmp_path / "policies"
        policies.mkdir()
        (policies / "a.feature").write_text("Feature: A\n", encoding="utf-8")
        with tarfile.open(bundle, "w:gz") as tar:
            tar.add(policies, arcname=".")
        client = MagicMock()
        client.pull.return_value = [str(bundle)]
        monkeypatch.setattr("src.compliance.oci_registry._client", lambda: client)
        out = tmp_path / "out"
        path = pull_policies("registry.example.com/p:1", output_dir=str(out))
        assert Path(path).exists()

    def test_resolve_features_dir_invalid(self):
        with pytest.raises(FileNotFoundError):
            resolve_features_dir("/not/policies/or/oci")


class TestBehaveSupport:
    def test_environment_hooks(self):
        context = SimpleNamespace(
            compliance_entities={},
            stash=[],
            step_mode=None,
            scenario_skipped=False,
            config=SimpleNamespace(
                userdata={
                    "pipeline": str(SAMPLE),
                    "include_nested": "true",
                }
            ),
        )
        behave_env.before_all(context)
        behave_env.before_scenario(context, SimpleNamespace())

    def test_given_and_when_then_steps(self):
        context = SimpleNamespace(
            compliance_entities={
                "jobs": [
                    {
                        "name": "build",
                        "values": {
                            "stage": "test",
                            "image": "alpine",
                            "extends": "template",
                        },
                    }
                ],
                "includes": [{"include_type": "local", "name": "x"}],
                "variables": [{"name": "VAR", "values": {"value": "1"}}],
                "workflow_rules": [{"name": "rule-1", "values": {"when": "always"}}],
                "project_settings": [],
                "project_ci_variables": [],
                "group_settings": [],
            },
            stash=[],
            step_mode=None,
            scenario_skipped=False,
            config=SimpleNamespace(userdata={"strict": "false"}),
            scenario=SimpleNamespace(skip=MagicMock()),
        )
        given_steps.given_any_job(context)
        given_steps.given_named_job(context, "build")
        given_steps.given_any_include(context)
        given_steps.given_include_type(context, "local")
        given_steps.given_any_variable(context)
        given_steps.given_any_workflow_rule(context)
        when_steps.when_it_has(context, "stage")
        when_steps.when_it_does_not_have(context, "missing")
        when_steps.when_property_is(context, "stage", "test")
        when_steps.when_property_matches(context, "image", "alpine")
        when_steps.when_key_is(context, "VAR")
        when_steps.when_name_not_starts_with(context, "z")
        then_steps.then_must_contain(context, "stage")
        then_steps.then_must_not_contain(context, "missing")
        then_steps.then_property_must_be(context, "stage", "test")
        then_steps.then_property_must_match(context, "image", "alpine")
        then_steps.then_property_must_not_match(context, "image", "latest")
        then_steps.then_property_not_null(context, "stage")
        then_steps.then_extends_includes(context, "template")

    def test_runner_env_and_path_guard(self, monkeypatch):
        with _temporary_gitlab_env(
            token="t", gitlab_url="https://x", project="p", group="g"
        ):
            assert os.environ.get("GITLAB_TOKEN") == "t"
        with pytest.raises(ValueError):
            _assert_within_directory("/tmp/a", "/tmp/b/outside.feature")


class TestMisc:
    def test_configure_logger(self):
        import io

        stream = io.StringIO()
        configure_logger("DEBUG", output=stream)
        configure_logger("INFO", output=stream)

    def test_release_sort_and_filter(self):
        tags = sort_tags(
            [SimpleNamespace(name="v2.0.0"), SimpleNamespace(name="not-semver")]
        )
        assert tags
        commits = filter_commits_since_tag([SimpleNamespace(id="1")], None)

    def test_render_status_icon_unknown(self):
        assert _status_icon("unknown") == "UNKNOWN"
        assert (
            render_compliance_report(
                __import__(
                    "src.compliance.models", fromlist=["ComplianceResult"]
                ).ComplianceResult(
                    success=True,
                    exit_code=0,
                    scenario_results=[],
                    scenarios=0,
                    passed=0,
                    failed=0,
                    skipped=0,
                ),
                ".gitlab-ci.yml",
                "policies",
                "unknown-format",
            )
            is None
        )
