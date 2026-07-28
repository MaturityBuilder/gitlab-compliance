"""Tests for shell-check markdown and HTML report renderers."""

from __future__ import annotations

from pathlib import Path

from src.compliance.models import ComplianceResult, ScenarioResult
from src.compliance.shell_render import (
    parse_shell_violations,
    render_shell_check_html,
    render_shell_check_markdown,
    render_shell_check_report,
)

FIXTURES = Path(__file__).parent / "fixtures" / "shell_check"
PIPELINE = str(FIXTURES / "bad-pipeline.yml")
POLICIES = "tests/compliance_policies/failing"


def _failed_scenario() -> ScenarioResult:
    return ScenarioResult(
        feature="shell-ci-conventions.feature",
        name="curl uses fail flag",
        status="failed",
        message=(
            "ASSERT FAILED: Job '.bad-template' "
            f"{FIXTURES / 'bad-pipeline.yml'}:4: curl without --fail/-f; "
            "Job 'bad-job' "
            f"{FIXTURES / 'bad-pipeline.yml'}:17: curl without --fail/-f "
            "via: extends:.bad-template"
        ),
        policy_id="GLCI-SHELL-CI-001",
        title="curl uses fail flag",
        description="curl must use --fail or -f",
    )


def _failed_result() -> ComplianceResult:
    return ComplianceResult(
        success=False,
        exit_code=1,
        scenario_results=[_failed_scenario()],
        scenarios=1,
        passed=0,
        failed=1,
        skipped=0,
    )


class TestParseShellViolations:
    def test_parses_structured_message(self):
        violations = parse_shell_violations(_failed_scenario().message)
        assert len(violations) == 2
        assert violations[0].job == ".bad-template"
        assert violations[0].message == "curl without --fail/-f"
        assert violations[1].inheritance == "extends:.bad-template"

    def test_preserves_semicolon_inside_message(self):
        message = "ASSERT FAILED: Job 'demo' file.yml:1: do not use foo; bar is wrong"
        violations = parse_shell_violations(message)
        assert len(violations) == 1
        assert violations[0].message == "do not use foo; bar is wrong"

    def test_parses_windows_style_path(self):
        message = r"ASSERT FAILED: Job 'demo' C:\repo\.gitlab-ci.yml:4: unquoted"
        violations = parse_shell_violations(message)
        assert len(violations) == 1
        assert violations[0].location == r"C:\repo\.gitlab-ci.yml:4"
        assert violations[0].message == "unquoted"


class TestRenderShellCheckMarkdown:
    def test_markdown_uses_shell_check_title(self):
        text = render_shell_check_markdown(_failed_result(), PIPELINE, POLICIES)
        assert "# Shell Check Report" in text
        assert "GitLab CI Compliance Report" not in text
        assert "**not** the external ShellCheck binary" in text

    def test_markdown_structures_findings_table(self):
        text = render_shell_check_markdown(_failed_result(), PIPELINE, POLICIES)
        assert "## Findings (1)" in text
        assert "Job" in text and "Location" in text and "Inheritance" in text
        assert "`.bad-template`" in text
        assert "`bad-pipeline.yml:4`" in text
        assert "extends:.bad-template" in text

    def test_markdown_includes_summary(self):
        text = render_shell_check_markdown(_failed_result(), PIPELINE, POLICIES)
        assert "## Summary" in text
        assert "Overall" in text and "FAIL" in text

    def test_markdown_includes_coverage_gaps(self):
        result = _failed_result()
        result.unresolved_includes = [
            {
                "include_type": "project",
                "reference": "group/project (ci.yml @ main)",
                "reason": "no_token",
                "source_file": ".gitlab-ci.yml",
                "line": 3,
            }
        ]
        text = render_shell_check_markdown(result, PIPELINE, POLICIES)
        assert "## Coverage gaps" in text
        assert "group/project" in text
        assert "missing authentication" in text


class TestRenderShellCheckHtml:
    def test_html_uses_shell_check_title(self):
        report = render_shell_check_html(_failed_result(), PIPELINE, POLICIES)
        assert "<title>Shell Check Report</title>" in report
        assert "Shell Check Failed" in report
        assert "GitLab CI Compliance Report" not in report

    def test_html_structures_findings_table(self):
        report = render_shell_check_html(_failed_result(), PIPELINE, POLICIES)
        assert "<h2>Findings (1)</h2>" in report
        assert "<th>Job</th><th>Location</th><th>Issue</th>" in report
        assert ".bad-template" in report
        assert "bad-pipeline.yml:4" in report

    def test_html_omits_empty_skipped_section(self):
        report = render_shell_check_html(_failed_result(), PIPELINE, POLICIES)
        assert "Skipped policies" not in report

    def test_html_includes_coverage_gaps(self):
        result = _failed_result()
        result.unresolved_includes = [
            {
                "include_type": "remote",
                "reference": "https://example.com/ci.yml",
                "reason": "fetch_failed",
                "detail": "404",
                "source_file": ".gitlab-ci.yml",
                "line": 2,
            }
        ]
        report = render_shell_check_html(result, PIPELINE, POLICIES)
        assert "Coverage gaps" in report
        assert "https://example.com/ci.yml" in report


class TestRenderShellCheckReport:
    def test_dispatch_markdown_and_html(self):
        result = _failed_result()
        assert render_shell_check_report(result, PIPELINE, POLICIES, "markdown")
        assert render_shell_check_report(result, PIPELINE, POLICIES, "html")
        assert render_shell_check_report(result, PIPELINE, POLICIES, "mr-comment")
        assert render_shell_check_report(result, PIPELINE, POLICIES, "console") is None

    def test_mr_comment_uses_shell_branding(self):
        text = render_shell_check_report(
            _failed_result(), PIPELINE, POLICIES, "mr-comment"
        )
        assert "### Shell Check Report" in text
        assert "GitLab CI Compliance Report" not in text
        assert "Findings" in text
        assert "`.bad-template`" in text
