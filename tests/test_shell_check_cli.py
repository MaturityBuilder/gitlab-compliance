"""CLI tests for gitlab-compliance shell-check."""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from src.gitlab_compliance import gitlab_compliance

FIXTURES = Path(__file__).parent / "fixtures" / "shell_check"


def test_shell_check_help():
    runner = CliRunner()
    result = runner.invoke(gitlab_compliance, ["shell-check", "--help"])
    assert result.exit_code == 0
    assert "not the ShellCheck tool" in result.output


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
    assert "GLCI-SHELL" in out.read_text(encoding="utf-8") or "FAIL" in out.read_text(
        encoding="utf-8"
    )
