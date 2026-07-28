"""CLI tests for gitlab-compliance shell-check."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from src.gitlab_compliance import gitlab_compliance

FIXTURES = Path(__file__).parent / "fixtures" / "shell_check"


def test_shell_check_help():
    runner = CliRunner()
    result = runner.invoke(gitlab_compliance, ["shell-check", "--help"])
    assert result.exit_code == 0
    assert "not the ShellCheck tool" in result.output
    assert "--gitlab-url" in result.output
    assert "--token" in result.output
    assert "--include-nested" in result.output


def test_shell_check_fails_on_bad_pipeline():
    runner = CliRunner()
    result = runner.invoke(
        gitlab_compliance,
        ["shell-check", "-p", str(FIXTURES / "bad-pipeline.yml")],
    )
    assert result.exit_code == 1


def test_shell_check_passes_on_good_pipeline():
    runner = CliRunner()
    result = runner.invoke(
        gitlab_compliance,
        ["shell-check", "-p", str(FIXTURES / "good-pipeline.yml")],
    )
    assert result.exit_code == 0, result.output
    assert "not the ShellCheck" in result.output or "GLCI-SHELL" in result.output


def test_shell_check_markdown_report(tmp_path):
    runner = CliRunner()
    out = tmp_path / "report.md"
    result = runner.invoke(
        gitlab_compliance,
        [
            "shell-check",
            "-p",
            str(FIXTURES / "bad-pipeline.yml"),
            "--format",
            "markdown",
            "-o",
            str(out),
        ],
    )
    assert result.exit_code == 1
    assert out.exists()
    text = out.read_text(encoding="utf-8")
    assert "Shell Check Report" in text
    assert "GLCI-SHELL" in text or "FAIL" in text
    assert "Job" in text and "Location" in text and "Inheritance" in text


def test_shell_check_html_report(tmp_path):
    runner = CliRunner()
    out = tmp_path / "report.html"
    result = runner.invoke(
        gitlab_compliance,
        [
            "shell-check",
            "-p",
            str(FIXTURES / "bad-pipeline.yml"),
            "--format",
            "html",
            "-o",
            str(out),
        ],
    )
    assert result.exit_code == 1
    assert out.exists()
    text = out.read_text(encoding="utf-8")
    assert "Shell Check Report" in text
    assert "<h2>Findings" in text


def test_shell_check_junit_report(tmp_path):
    runner = CliRunner()
    out = tmp_path / "report.xml"
    result = runner.invoke(
        gitlab_compliance,
        [
            "shell-check",
            "-p",
            str(FIXTURES / "bad-pipeline.yml"),
            "--format",
            "junit",
            "-o",
            str(out),
        ],
    )
    assert result.exit_code == 1
    assert out.exists()
    text = out.read_text(encoding="utf-8")
    assert 'name="shell-check"' in text
    assert "<failure" in text


@pytest.mark.parametrize("pipeline", ["string-include.yml", "dict-include.yml"])
def test_shell_check_detects_pinning_in_nested_includes(pipeline):
    runner = CliRunner()
    result = runner.invoke(
        gitlab_compliance,
        ["shell-check", "-p", str(FIXTURES / pipeline)],
    )
    assert result.exit_code == 1, result.output
    assert (
        "GLCI-SHELL-PIN-005" in result.output
        or "apt packages must be version-pinned" in result.output
    )
