"""CLI tests for gitlab-compliance supply-chain."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from src.compliance.builtin_policies import BUILTIN_SUPPLY_CHAIN_POLICIES_DIR
from src.gitlab_compliance import gitlab_compliance

REPO_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_PIPELINE = REPO_ROOT / "examples" / "sample-files" / ".gitlab-ci.yml"


def test_supply_chain_help():
    runner = CliRunner()
    result = runner.invoke(gitlab_compliance, ["supply-chain", "--help"])
    assert result.exit_code == 0
    assert "supply-chain pinning policies" in result.output
    assert "--fix" in result.output
    assert "mutates YAML" in result.output
    assert "--resolve-external-includes" in result.output


def test_check_help_includes_resolve_external_includes():
    runner = CliRunner()
    result = runner.invoke(gitlab_compliance, ["check", "--help"])
    assert result.exit_code == 0
    assert "--resolve-external-includes" in result.output
    assert "junit" in result.output


def test_check_fix_without_token_exits_with_error():
    runner = CliRunner()
    result = runner.invoke(
        gitlab_compliance,
        ["check", "--with-supply-chain", "--fix", "-p", str(SAMPLE_PIPELINE)],
    )
    assert result.exit_code == 2
    assert "token" in result.output.lower()


def test_supply_chain_help_includes_create_mr():
    runner = CliRunner()
    result = runner.invoke(gitlab_compliance, ["supply-chain", "--help"])
    assert result.exit_code == 0
    assert "--create-mr" in result.output


def test_supply_chain_create_mr_requires_fix():
    runner = CliRunner()
    result = runner.invoke(
        gitlab_compliance,
        [
            "supply-chain",
            "-p",
            str(SAMPLE_PIPELINE),
            "--create-mr",
            "--token",
            "secret",
            "--project",
            "org/project",
        ],
    )
    assert result.exit_code == 2
    assert "--create-mr requires --fix and/or --fix-policies" in result.output


def test_check_help_includes_with_supply_chain_and_fix():
    runner = CliRunner()
    result = runner.invoke(gitlab_compliance, ["check", "--help"])
    assert result.exit_code == 0
    assert "--with-supply-chain" in result.output
    assert "--fix" in result.output
    assert "--fix-supply-chain" in result.output


def test_supply_chain_runs_packaged_policies():
    runner = CliRunner()
    result = runner.invoke(
        gitlab_compliance,
        ["supply-chain", "-p", str(SAMPLE_PIPELINE)],
    )
    assert result.exit_code in {0, 1}
    assert "GLCI-BUILTIN-IMAGE-PINNING" in result.output
    assert "GLCI-BUILTIN-INCLUDE-VERSIONS" in result.output
    assert "gitlab-compliance supply-chain" in result.output


def test_supply_chain_without_fix_does_not_mutate_yaml(tmp_path):
    pipeline = tmp_path / ".gitlab-ci.yml"
    original = (
        "include:\n"
        "  - project: org/templates\n"
        "    ref: main\n"
        "    file: ci.yml\n"
        "job:\n"
        "  script:\n"
        "    - echo hi\n"
    )
    pipeline.write_text(original, encoding="utf-8")

    runner = CliRunner()
    with patch(
        "src.compliance.supply_chain_fix.apply_supply_chain_fixes"
    ) as apply_fixes:
        result = runner.invoke(
            gitlab_compliance,
            ["supply-chain", "-p", str(pipeline)],
        )

    assert result.exit_code in {0, 1}
    apply_fixes.assert_not_called()
    assert pipeline.read_text(encoding="utf-8") == original


def test_supply_chain_fix_invokes_yaml_remediation(tmp_path):
    pipeline = tmp_path / ".gitlab-ci.yml"
    pipeline.write_text("job:\n  script:\n    - echo hi\n", encoding="utf-8")

    runner = CliRunner()
    with patch(
        "src.compliance.supply_chain_fix.apply_supply_chain_fixes",
        return_value=["pinned image: nginx"],
    ) as apply_fixes:
        result = runner.invoke(
            gitlab_compliance,
            ["supply-chain", "-p", str(pipeline), "--fix", "--token", "secret"],
        )

    assert result.exit_code in {0, 1}
    apply_fixes.assert_called_once()


def test_check_with_supply_chain_only():
    runner = CliRunner()
    result = runner.invoke(
        gitlab_compliance,
        ["check", "--with-supply-chain", "-p", str(SAMPLE_PIPELINE)],
    )
    assert result.exit_code in {0, 1}
    assert "GLCI-BUILTIN-IMAGE-PINNING" in result.output
    assert "GLCI-BUILTIN-INCLUDE-VERSIONS" in result.output


def test_builtin_supply_chain_dir_contains_pinning_policies():
    policy_files = list(Path(BUILTIN_SUPPLY_CHAIN_POLICIES_DIR).glob("*.feature"))
    names = {path.name for path in policy_files}
    assert names == {
        "image-pinning.feature",
        "include-versions.feature",
        "service-pinning.feature",
    }
