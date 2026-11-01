"""Fixture-backed integration tests for ``gitlab-compliance lock``."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from src.compliance.lockfile import build_lockfile, verify_lockfile, write_lockfile
from src.gitlab_compliance import gitlab_compliance

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "lock"
FULL = FIXTURES / "full-inventory" / ".gitlab-ci.yml"
MINIMAL = FIXTURES / "minimal" / ".gitlab-ci.yml"
BROKEN = FIXTURES / "broken-local" / ".gitlab-ci.yml"
POLICIES = FIXTURES / "policies"
REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


class TestLockFixtureInventory:
    def test_full_inventory_fixture_shapes_lock(self):
        lockfile = build_lockfile(
            str(FULL), resolve_external_includes=False, enrich=False
        )
        inventory = lockfile["inventory"]
        types = {item["type"] for item in inventory["includes"]}
        assert {"local", "project", "component", "template", "remote"} <= types
        assert any(item["source"] == "service" for item in inventory["images"])
        assert any(item["digest"] for item in inventory["images"])
        assert any(item["kind"] == "trigger" for item in inventory["externalSteps"])
        assert inventory["pipeline"]["variableKeys"]
        assert inventory["pipeline"]["workflowRuleCount"] >= 1

    def test_policies_fixture_changes_fingerprint(self):
        without = build_lockfile(
            str(MINIMAL), resolve_external_includes=False, enrich=False
        )
        with_policies = build_lockfile(
            str(MINIMAL),
            resolve_external_includes=False,
            enrich=False,
            features_dir=str(POLICIES),
        )
        assert without["fingerprint"] != with_policies["fingerprint"]

    def test_broken_local_include_is_inventoried(self):
        inventory = build_lockfile(
            str(BROKEN), resolve_external_includes=False, enrich=False
        )["inventory"]
        locals_ = [i for i in inventory["includes"] if i["type"] == "local"]
        assert locals_
        assert locals_[0]["resolved"] is False


def _copy_full_fixture(tmp_path: Path) -> Path:
    """Copy the full-inventory fixture into tmp_path so tests can mutate it."""
    import shutil

    dest = tmp_path / "full-inventory"
    shutil.copytree(FIXTURES / "full-inventory", dest)
    return dest / ".gitlab-ci.yml"


class TestLockCliIntegration:
    def test_generate_verify_update_roundtrip_on_fixture(self, runner, tmp_path):
        pipeline = _copy_full_fixture(tmp_path)
        lock_path = tmp_path / ".gitlab-ci.lock"
        generate = runner.invoke(
            gitlab_compliance,
            [
                "lock",
                "generate",
                "-p",
                str(pipeline),
                "-l",
                str(lock_path),
                "-f",
                str(POLICIES),
                "--no-resolve-external-includes",
                "--no-enrich",
                "--verbose",
            ],
        )
        assert generate.exit_code == 0, generate.output
        assert "Coverage" in generate.output
        assert lock_path.is_file()

        verify = runner.invoke(
            gitlab_compliance,
            [
                "lock",
                "verify",
                "-p",
                str(pipeline),
                "-l",
                str(lock_path),
                "-f",
                str(POLICIES),
                "--no-resolve-external-includes",
                "--no-enrich",
                "--json",
            ],
        )
        assert verify.exit_code == 0, verify.output
        payload = json.loads(verify.output)
        assert payload["matches"] is True
        assert payload["health"]["letter"] in list("ABCDE")

        # Drift then update.
        pipeline.write_text(
            pipeline.read_text(encoding="utf-8") + "\n# fixture-drift\n",
            encoding="utf-8",
        )
        drifted = runner.invoke(
            gitlab_compliance,
            [
                "lock",
                "verify",
                "-p",
                str(pipeline),
                "-l",
                str(lock_path),
                "-f",
                str(POLICIES),
                "--no-resolve-external-includes",
                "--no-enrich",
            ],
        )
        assert drifted.exit_code == 1
        assert "Drift" in drifted.output or "drift" in drifted.output.lower()

        update = runner.invoke(
            gitlab_compliance,
            [
                "lock",
                "update",
                "-p",
                str(pipeline),
                "-l",
                str(lock_path),
                "-f",
                str(POLICIES),
                "--no-resolve-external-includes",
                "--no-enrich",
                "--quiet",
            ],
        )
        assert update.exit_code == 0, update.output
        assert update.output.strip().startswith("sha256:")

    def test_fingerprint_from_lock_dotenv_and_verbose(self, runner, tmp_path):
        lock_path = tmp_path / ".gitlab-ci.lock"
        dotenv = tmp_path / "lock.env"
        write_lockfile(
            build_lockfile(str(MINIMAL), resolve_external_includes=False, enrich=False),
            lock_path,
        )
        result = runner.invoke(
            gitlab_compliance,
            [
                "lock",
                "fingerprint",
                "--from-lock",
                "-l",
                str(lock_path),
                "--dotenv",
                str(dotenv),
                "--verbose",
            ],
        )
        assert result.exit_code == 0, result.output
        assert "Fingerprint" in result.output or "sha256:" in result.output
        assert dotenv.is_file()
        assert "GITLAB_COMPLIANCE_LOCK_FINGERPRINT=" in dotenv.read_text(
            encoding="utf-8"
        )

    def test_enrich_without_token_still_runs(self, runner, tmp_path):
        """Image digest enrichment does not require a GitLab token."""
        lock_path = tmp_path / ".gitlab-ci.lock"
        with patch(
            "src.compliance.image_versions.enrich_container_images_with_releases",
            side_effect=lambda items, **kwargs: items,
        ):
            result = runner.invoke(
                gitlab_compliance,
                [
                    "lock",
                    "generate",
                    "-p",
                    str(MINIMAL),
                    "-l",
                    str(lock_path),
                    "--enrich",
                    "--no-resolve-external-includes",
                    "--quiet",
                ],
                env={
                    **os.environ,
                    "GITLAB_TOKEN": "",
                    "CI_JOB_TOKEN": "",
                },
            )
        assert result.exit_code == 0, result.output
        assert lock_path.is_file()

    def test_verify_missing_lock_exits_2(self, runner, tmp_path):
        result = runner.invoke(
            gitlab_compliance,
            [
                "lock",
                "verify",
                "-p",
                str(MINIMAL),
                "-l",
                str(tmp_path / "missing.lock"),
                "--no-resolve-external-includes",
                "--no-enrich",
            ],
        )
        assert result.exit_code == 2

    def test_fingerprint_json(self, runner):
        result = runner.invoke(
            gitlab_compliance,
            [
                "lock",
                "fingerprint",
                "-p",
                str(MINIMAL),
                "--no-resolve-external-includes",
                "--no-enrich",
                "--json",
            ],
        )
        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)
        assert payload["fingerprint"].startswith("sha256:")


class TestLockSubprocessIntegration:
    def test_module_entrypoint_lock_generate(self, tmp_path):
        lock_path = tmp_path / ".gitlab-ci.lock"
        proc = subprocess.run(
            [
                sys.executable,
                "-m",
                "src.gitlab_compliance",
                "lock",
                "generate",
                "-p",
                str(MINIMAL),
                "-l",
                str(lock_path),
                "--no-resolve-external-includes",
                "--no-enrich",
                "--json",
            ],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        assert proc.returncode == 0, proc.stderr + proc.stdout
        payload = json.loads(proc.stdout)
        assert payload["command"] == "generate"
        assert lock_path.is_file()

        verify = subprocess.run(
            [
                sys.executable,
                "-m",
                "src.gitlab_compliance",
                "lock",
                "verify",
                "-p",
                str(MINIMAL),
                "-l",
                str(lock_path),
                "--no-resolve-external-includes",
                "--no-enrich",
                "--quiet",
            ],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        assert verify.returncode == 0, verify.stderr + verify.stdout
        assert verify.stdout.strip().startswith("sha256:")

    def test_api_verify_matches_cli_fingerprint(self, tmp_path):
        lock_path = tmp_path / ".gitlab-ci.lock"
        lockfile = build_lockfile(
            str(FULL), resolve_external_includes=False, enrich=False
        )
        write_lockfile(lockfile, lock_path)
        result = verify_lockfile(
            str(FULL), lock_path, resolve_external_includes=False, enrich=False
        )
        assert result["matches"] is True
        assert result["actualFingerprint"] == lockfile["fingerprint"]
