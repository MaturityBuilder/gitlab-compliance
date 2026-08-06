"""Integration tests for complex shell-check fixtures and CLI flags."""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from src.compliance.runner import run_compliance
from src.gitlab_compliance import gitlab_compliance

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "shell_check"
GOOD = FIXTURES / "complex-good-pipeline.yml"
BAD = FIXTURES / "complex-bad-pipeline.yml"

EXPECTED_FAMILIES = (
    "GLCI-BUILTIN-SHELL-QUOTE",
    "GLCI-BUILTIN-SHELL-ERR",
    "GLCI-BUILTIN-SHELL-FILE",
    "GLCI-BUILTIN-SHELL-PIPE",
    "GLCI-BUILTIN-SHELL-SAFE",
    "GLCI-BUILTIN-SHELL-PIN",
    "GLCI-BUILTIN-SHELL-PORT",
    "GLCI-BUILTIN-SHELL-SUB",
    "GLCI-BUILTIN-SHELL-CI",
    "GLCI-BUILTIN-SHELL-TEST",
    "GLCI-BUILTIN-SHELL-REF",
)


def test_complex_good_pipeline_passes_all_shell_policies():
    result = run_compliance(
        features_dir=None,
        pipeline_file=str(GOOD),
        with_shell_check=True,
        output_format="markdown",
    )
    assert result.failed == 0
    assert result.passed > 0
    assert result.success


def test_complex_bad_pipeline_fails_all_shell_policy_families():
    result = run_compliance(
        features_dir=None,
        pipeline_file=str(BAD),
        with_shell_check=True,
        output_format="markdown",
    )
    assert result.failed > 0
    assert not result.success
    failed_ids = {
        scenario.policy_id
        for scenario in result.scenario_results
        if scenario.status == "failed" and scenario.policy_id
    }
    for family in EXPECTED_FAMILIES:
        assert any(
            policy_id.startswith(family) for policy_id in failed_ids
        ), f"Expected a failure in family {family}, got {sorted(failed_ids)}"


def test_shell_check_verbose_includes_found_value(tmp_path):
    out = tmp_path / "verbose.md"
    runner = CliRunner()
    result = runner.invoke(
        gitlab_compliance,
        [
            "shell-check",
            "-p",
            str(BAD),
            "-v",
            "--format",
            "markdown",
            "-o",
            str(out),
        ],
    )
    assert result.exit_code == 1
    text = out.read_text(encoding="utf-8")
    assert "found: echo $UNQUOTED" in text
    assert "found: apk add curl" in text


def test_shell_check_failures_only_omits_passed_section(tmp_path):
    out = tmp_path / "failures.md"
    runner = CliRunner()
    result = runner.invoke(
        gitlab_compliance,
        [
            "shell-check",
            "-p",
            str(BAD),
            "--failures-only",
            "--format",
            "markdown",
            "-o",
            str(out),
        ],
    )
    assert result.exit_code == 1
    text = out.read_text(encoding="utf-8")
    assert "## Findings" in text
    assert "## Passed policies" not in text


def test_shell_check_policy_filter_runs_selected_ids_only():
    result = run_compliance(
        features_dir=None,
        pipeline_file=str(BAD),
        with_shell_check=True,
        output_format="markdown",
        policies=["GLCI-BUILTIN-SHELL-PIN-03", "GLCI-BUILTIN-SHELL-QUOTE-01"],
    )
    assert result.scenarios == 2
    ids = {scenario.policy_id for scenario in result.scenario_results}
    assert ids == {"GLCI-BUILTIN-SHELL-PIN-03", "GLCI-BUILTIN-SHELL-QUOTE-01"}
    assert result.failed == 2


def test_shell_check_policy_glob_and_feature_stem():
    pin_result = run_compliance(
        features_dir=None,
        pipeline_file=str(BAD),
        with_shell_check=True,
        output_format="markdown",
        policies=["GLCI-BUILTIN-SHELL-PIN*"],
    )
    assert pin_result.scenarios == 10
    assert all(
        (scenario.policy_id or "").startswith("GLCI-BUILTIN-SHELL-PIN")
        for scenario in pin_result.scenario_results
    )

    quote_result = run_compliance(
        features_dir=None,
        pipeline_file=str(GOOD),
        with_shell_check=True,
        output_format="markdown",
        policies=["shell-quoting"],
    )
    assert quote_result.scenarios == 4
    assert quote_result.failed == 0
    assert all(
        (scenario.policy_id or "").startswith("GLCI-BUILTIN-SHELL-QUOTE")
        for scenario in quote_result.scenario_results
    )


def test_shell_check_policy_unknown_selector_errors():
    import pytest

    with pytest.raises(ValueError, match="No policies matched selectors"):
        run_compliance(
            features_dir=None,
            pipeline_file=str(BAD),
            with_shell_check=True,
            output_format="markdown",
            policies=["NOPE-NOT-A-POLICY"],
        )
