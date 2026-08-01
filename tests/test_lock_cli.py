"""CLI tests for gitlab-compliance lock."""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from src.compliance.lockfile import FINGERPRINT_ENV_KEY
from src.gitlab_compliance import gitlab_compliance


def _pipeline(tmp_path: Path) -> Path:
    pipeline = tmp_path / ".gitlab-ci.yml"
    pipeline.write_text(
        "job:\n  image: alpine:3.19\n  script:\n    - echo hi\n",
        encoding="utf-8",
    )
    return pipeline


def test_lock_help_lists_subcommands():
    runner = CliRunner()
    result = runner.invoke(gitlab_compliance, ["lock", "--help"])
    assert result.exit_code == 0
    assert "generate" in result.output
    assert "verify" in result.output
    assert "update" in result.output
    assert "fingerprint" in result.output
    assert "inventory" in result.output.lower()


def test_lock_generate_verify_fingerprint_roundtrip(tmp_path):
    pipeline = _pipeline(tmp_path)
    lock_file = tmp_path / ".gitlab-ci.lock"
    runner = CliRunner()

    generate = runner.invoke(
        gitlab_compliance,
        [
            "lock",
            "generate",
            "-p",
            str(pipeline),
            "-l",
            str(lock_file),
            "--no-resolve-external-includes",
        ],
    )
    assert generate.exit_code == 0, generate.output
    assert lock_file.is_file()
    payload = json.loads(lock_file.read_text(encoding="utf-8"))
    assert payload["fingerprint"].startswith("sha256:")
    assert "inventory" in payload

    verify = runner.invoke(
        gitlab_compliance,
        [
            "lock",
            "verify",
            "-p",
            str(pipeline),
            "-l",
            str(lock_file),
            "--no-resolve-external-includes",
        ],
    )
    assert verify.exit_code == 0, verify.output

    fingerprint = runner.invoke(
        gitlab_compliance,
        [
            "lock",
            "fingerprint",
            "-p",
            str(pipeline),
            "--no-resolve-external-includes",
        ],
    )
    assert fingerprint.exit_code == 0
    assert fingerprint.output.strip() == payload["fingerprint"]


def test_lock_verify_detects_drift(tmp_path):
    pipeline = _pipeline(tmp_path)
    lock_file = tmp_path / ".gitlab-ci.lock"
    runner = CliRunner()
    runner.invoke(
        gitlab_compliance,
        [
            "lock",
            "generate",
            "-p",
            str(pipeline),
            "-l",
            str(lock_file),
            "--no-resolve-external-includes",
        ],
    )
    pipeline.write_text(
        "job:\n  image: alpine:3.20\n  script:\n    - echo hi\n",
        encoding="utf-8",
    )
    result = runner.invoke(
        gitlab_compliance,
        [
            "lock",
            "verify",
            "-p",
            str(pipeline),
            "-l",
            str(lock_file),
            "--no-resolve-external-includes",
        ],
    )
    assert result.exit_code == 1
    assert "does not match" in result.output.lower() or "Lock drift" in result.output


def test_lock_fingerprint_dotenv_and_from_lock(tmp_path):
    pipeline = _pipeline(tmp_path)
    lock_file = tmp_path / ".gitlab-ci.lock"
    dotenv = tmp_path / "lock.env"
    runner = CliRunner()
    runner.invoke(
        gitlab_compliance,
        [
            "lock",
            "generate",
            "-p",
            str(pipeline),
            "-l",
            str(lock_file),
            "--no-resolve-external-includes",
        ],
    )
    result = runner.invoke(
        gitlab_compliance,
        [
            "lock",
            "fingerprint",
            "--from-lock",
            "-l",
            str(lock_file),
            "--dotenv",
            str(dotenv),
        ],
    )
    assert result.exit_code == 0
    assert dotenv.read_text(encoding="utf-8").startswith(f"{FINGERPRINT_ENV_KEY}=")


def test_lock_update_rewrites_file(tmp_path):
    pipeline = _pipeline(tmp_path)
    lock_file = tmp_path / ".gitlab-ci.lock"
    runner = CliRunner()
    runner.invoke(
        gitlab_compliance,
        [
            "lock",
            "generate",
            "-p",
            str(pipeline),
            "-l",
            str(lock_file),
            "--no-resolve-external-includes",
        ],
    )
    original = lock_file.read_text(encoding="utf-8")
    pipeline.write_text(
        "job:\n  image: alpine:3.20\n  script:\n    - echo hi\n",
        encoding="utf-8",
    )
    update = runner.invoke(
        gitlab_compliance,
        [
            "lock",
            "update",
            "-p",
            str(pipeline),
            "-l",
            str(lock_file),
            "--no-resolve-external-includes",
        ],
    )
    assert update.exit_code == 0, update.output
    assert lock_file.read_text(encoding="utf-8") != original


def test_lock_generate_missing_pipeline_exits_2(tmp_path):
    runner = CliRunner()
    result = runner.invoke(
        gitlab_compliance,
        [
            "lock",
            "generate",
            "-p",
            str(tmp_path / "missing.yml"),
            "-l",
            str(tmp_path / ".gitlab-ci.lock"),
        ],
    )
    assert result.exit_code == 2
