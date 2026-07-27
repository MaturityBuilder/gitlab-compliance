"""CLI tests for gitlab-compliance supply-chain."""

from __future__ import annotations

from pathlib import Path

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


def test_check_help_includes_with_supply_chain():
    runner = CliRunner()
    result = runner.invoke(gitlab_compliance, ["check", "--help"])
    assert result.exit_code == 0
    assert "--with-supply-chain" in result.output


def test_supply_chain_runs_packaged_policies():
    runner = CliRunner()
    result = runner.invoke(
        gitlab_compliance,
        ["supply-chain", "-p", str(SAMPLE_PIPELINE)],
    )
    assert result.exit_code in {0, 1}
    assert "GLCI-IMAGE-PINNING" in result.output or "GLCI-INCLUDE" in result.output


def test_check_with_supply_chain_only():
    runner = CliRunner()
    result = runner.invoke(
        gitlab_compliance,
        ["check", "--with-supply-chain", "-p", str(SAMPLE_PIPELINE)],
    )
    assert result.exit_code in {0, 1}
    assert "GLCI-IMAGE-PINNING" in result.output or "GLCI-INCLUDE" in result.output


def test_builtin_supply_chain_dir_contains_pinning_policies():
    policy_files = list(Path(BUILTIN_SUPPLY_CHAIN_POLICIES_DIR).glob("*.feature"))
    names = {path.name for path in policy_files}
    assert "image-pinning.feature" in names
    assert "include-versions.feature" in names
