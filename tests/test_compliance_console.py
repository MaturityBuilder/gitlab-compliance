"""Tests for Rich compliance console helpers and CLI error UX."""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner
from rich.console import Console

from src.compliance.console import (
    _hint_for_message,
    get_console,
    print_error,
    print_info,
    print_success,
    print_warning,
    render_compliance_console,
)
from src.compliance.models import ComplianceResult, ScenarioResult
from src.gitlab_compliance import check

PASSING = Path(__file__).resolve().parent / "compliance_policies" / "passing"
SAMPLE = (
    Path(__file__).resolve().parents[1] / "examples" / "sample-files" / ".gitlab-ci.yml"
)


def _result(
    *,
    success: bool = False,
    with_description: bool = True,
    with_message: bool = True,
    empty_scenarios: bool = False,
    unknown_status: bool = False,
    no_policy_id: bool = False,
    skipped_message: str = "",
) -> ComplianceResult:
    if empty_scenarios:
        return ComplianceResult(
            success=success,
            exit_code=0 if success else 1,
            features=0,
            scenarios=0,
            passed=0,
            failed=0,
            skipped=0,
            scenario_results=[],
        )

    failed = ScenarioResult(
        feature="security.feature",
        name="pin images",
        status="unknown" if unknown_status else ("failed" if not success else "passed"),
        message="image is latest" if with_message else "",
        description="Pin digests" if with_description else "",
        policy_id="" if no_policy_id else "POL-1",
        title="Images must be pinned",
    )
    skipped = ScenarioResult(
        feature="security.feature",
        name="skip me",
        status="skipped",
        message=skipped_message,
        policy_id="" if no_policy_id else "POL-2",
        title="",
    )
    return ComplianceResult(
        success=success,
        exit_code=0 if success else 1,
        features=1,
        scenarios=2,
        passed=1 if success else 0,
        failed=0 if success else 1,
        skipped=1,
        scenario_results=[failed, skipped],
    )


class TestRichConsoleHelpers:
    def test_hint_lookup_and_miss(self):
        assert _hint_for_message("--create-mr requires --fix and/or --fix-policies")
        assert _hint_for_message("totally unknown message") is None

    def test_get_console_with_and_without_width(self):
        assert isinstance(get_console(), Console)
        assert get_console(width=40).width == 40
        assert get_console(width=120).width == 120

    def test_print_error_includes_hint(self):
        console = Console(width=80, record=True, force_terminal=True)
        print_error(
            "--create-mr requires --fix and/or --fix-policies",
            console=console,
        )
        text = console.export_text()
        assert "Error" in text
        assert "--create-mr requires --fix and/or --fix-policies" in text
        assert "Hint:" in text
        assert "--fix --create-mr" in text

    def test_print_error_explicit_hint_overrides(self):
        console = Console(width=80, record=True, force_terminal=True)
        print_error("boom", hint="try again", console=console)
        text = console.export_text()
        assert "boom" in text
        assert "try again" in text

    def test_print_error_without_hint(self):
        console = Console(width=80, record=True, force_terminal=True)
        print_error("unmatched failure", hint="", console=console)
        text = console.export_text()
        assert "unmatched failure" in text
        assert "Hint:" not in text

    def test_print_warning_success_info(self):
        console = Console(width=80, record=True, force_terminal=True)
        print_warning("skipped file", console=console)
        print_success("created MR", console=console)
        print_info("heads up", console=console)
        text = console.export_text()
        assert "Warning" in text
        assert "Success" in text
        assert "Info" in text
        assert "created MR" in text
        assert "heads up" in text

    def test_render_compliance_console_wide_failures(self):
        console = Console(
            width=120, height=40, record=True, force_terminal=True, soft_wrap=True
        )
        render_compliance_console(
            _result(success=False),
            ".gitlab-ci.yml",
            "policies/",
            console=console,
        )
        text = console.export_text()
        assert "Compliance Failed" in text
        assert "POL-1" in text
        assert "Images must be pinned" in text
        assert "Failures" in text
        assert "Skipped" in text
        assert "Features" in text

    def test_render_compliance_console_medium_width(self):
        console = Console(
            width=80, height=40, record=True, force_terminal=True, soft_wrap=True
        )
        render_compliance_console(
            _result(success=False, no_policy_id=True),
            ".gitlab-ci.yml",
            "policies/",
            console=console,
        )
        text = console.export_text()
        assert "Compliance Failed" in text
        assert "security.feature" in text or "Images must be pinned" in text

    def test_render_compliance_console_narrow(self):
        console = Console(
            width=40, height=40, record=True, force_terminal=True, soft_wrap=True
        )
        render_compliance_console(
            _result(success=True, with_description=False, with_message=False),
            ".gitlab-ci.yml",
            "policies/",
            console=console,
        )
        text = console.export_text()
        assert "Compliance Passed" in text
        assert "Images must be pinned" in text or "pin images" in text

    def test_render_empty_scenarios_and_unknown_status(self):
        console = Console(
            width=120, height=40, record=True, force_terminal=True, soft_wrap=True
        )
        render_compliance_console(
            _result(success=True, empty_scenarios=True),
            "ci.yml",
            "policies/",
            console=console,
        )
        render_compliance_console(
            _result(success=False, unknown_status=True),
            "ci.yml",
            "policies/",
            console=console,
        )
        text = console.export_text()
        assert "Compliance Passed" in text
        assert "UNKNOWN" in text

    def test_render_failure_description_without_message(self):
        console = Console(
            width=120, height=40, record=True, force_terminal=True, soft_wrap=True
        )
        render_compliance_console(
            _result(
                success=False,
                with_description=True,
                with_message=False,
                skipped_message="no matching jobs",
            ),
            "ci.yml",
            "policies/",
            console=console,
        )
        text = console.export_text()
        assert "Pin digests" in text
        assert "no matching jobs" in text
        assert "image is latest" not in text

    def test_render_failure_message_without_description(self):
        console = Console(
            width=120, height=40, record=True, force_terminal=True, soft_wrap=True
        )
        render_compliance_console(
            _result(success=False, with_description=False, with_message=True),
            "ci.yml",
            "policies/",
            console=console,
        )
        text = console.export_text()
        assert "image is latest" in text
        assert "Pin digests" not in text

    def test_render_uses_default_console(self):
        render_compliance_console(_result(success=True), "ci.yml", "policies/")

    def test_print_helpers_use_default_console(self):
        print_error("unmatched")
        print_warning("warn")
        print_success("ok")
        print_info("info")

    def test_check_cli_renders_rich_error_panel(self):
        runner = CliRunner()
        result = runner.invoke(
            check,
            [
                "--features",
                str(PASSING),
                "--pipeline",
                str(SAMPLE),
                "--create-mr",
            ],
        )
        assert result.exit_code == 2
        assert "--create-mr requires --fix and/or --fix-policies" in result.output
        assert "Hint:" in result.output

    def test_check_cli_missing_pipeline_rich_error(self, tmp_path):
        runner = CliRunner()
        result = runner.invoke(
            check,
            [
                "--features",
                str(PASSING),
                "--pipeline",
                str(tmp_path / "missing.yml"),
            ],
        )
        assert result.exit_code == 2
        assert "Pipeline file not found" in result.output
        assert "Hint:" in result.output

    def test_check_cli_markdown_pass_writes_report(self, tmp_path):
        out = tmp_path / "report.md"
        runner = CliRunner()
        result = runner.invoke(
            check,
            [
                "--features",
                str(PASSING),
                "--pipeline",
                str(SAMPLE),
                "--format",
                "markdown",
                "--output-file",
                str(out),
            ],
        )
        assert result.exit_code == 0
        assert out.is_file()
        assert "Report written" in result.output
        assert "Compliance passed" in result.output

    def test_check_cli_markdown_fail_shows_error_panel(self):
        failing = Path(__file__).resolve().parent / "compliance_policies" / "failing"
        runner = CliRunner()
        result = runner.invoke(
            check,
            [
                "--features",
                str(failing),
                "--pipeline",
                str(SAMPLE),
                "--format",
                "markdown",
            ],
        )
        assert result.exit_code == 1
        assert "Compliance failed" in result.output
        assert "Review the report" in result.output
