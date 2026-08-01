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


def test_lock_generate_help_includes_modern_flags():
    runner = CliRunner()
    result = runner.invoke(gitlab_compliance, ["lock", "generate", "--help"])
    assert result.exit_code == 0
    assert "--verbose" in result.output
    assert "--quiet" in result.output
    assert "--json" in result.output


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
            "--no-enrich",
        ],
    )
    assert generate.exit_code == 0, generate.output
    assert lock_file.is_file()
    assert "Inventory locked" in generate.output or "Coverage" in generate.output
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
            "--no-enrich",
        ],
    )
    assert verify.exit_code == 0, verify.output
    assert "verified" in verify.output.lower() or "Coverage" in verify.output

    fingerprint = runner.invoke(
        gitlab_compliance,
        [
            "lock",
            "fingerprint",
            "-p",
            str(pipeline),
            "--no-resolve-external-includes",
            "--no-enrich",
            "--quiet",
        ],
    )
    assert fingerprint.exit_code == 0
    assert fingerprint.output.strip() == payload["fingerprint"]


def test_lock_generate_json_and_quiet(tmp_path):
    pipeline = _pipeline(tmp_path)
    lock_file = tmp_path / ".gitlab-ci.lock"
    runner = CliRunner()
    json_result = runner.invoke(
        gitlab_compliance,
        [
            "lock",
            "generate",
            "-p",
            str(pipeline),
            "-l",
            str(lock_file),
            "--no-resolve-external-includes",
            "--no-enrich",
            "--json",
        ],
    )
    assert json_result.exit_code == 0, json_result.output
    payload = json.loads(json_result.output)
    assert payload["command"] == "generate"
    assert payload["fingerprint"].startswith("sha256:")

    quiet = runner.invoke(
        gitlab_compliance,
        [
            "lock",
            "verify",
            "-p",
            str(pipeline),
            "-l",
            str(lock_file),
            "--no-resolve-external-includes",
            "--no-enrich",
            "--quiet",
        ],
    )
    assert quiet.exit_code == 0
    assert quiet.output.strip().startswith("sha256:")


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
            "--no-enrich",
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
            "--no-enrich",
        ],
    )
    assert result.exit_code == 1
    assert (
        "drift" in result.output.lower()
        or "does not match" in result.output.lower()
        or "Next steps" in result.output
    )


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
            "--no-enrich",
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
            "--no-enrich",
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
            "--no-enrich",
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


def test_lock_update_and_fingerprint_missing_paths(tmp_path):
    runner = CliRunner()
    missing = str(tmp_path / "missing.yml")
    update = runner.invoke(
        gitlab_compliance,
        ["lock", "update", "-p", missing, "-l", str(tmp_path / "x.lock")],
    )
    assert update.exit_code == 2

    fingerprint = runner.invoke(
        gitlab_compliance,
        ["lock", "fingerprint", "-p", missing],
    )
    assert fingerprint.exit_code == 2

    from_lock = runner.invoke(
        gitlab_compliance,
        [
            "lock",
            "fingerprint",
            "--from-lock",
            "-l",
            str(tmp_path / "missing.lock"),
        ],
    )
    assert from_lock.exit_code == 2


def test_lock_verify_missing_pipeline_with_existing_lock(tmp_path):
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
            "--no-enrich",
            "--quiet",
        ],
    )
    result = runner.invoke(
        gitlab_compliance,
        [
            "lock",
            "verify",
            "-p",
            str(tmp_path / "gone.yml"),
            "-l",
            str(lock_file),
            "--no-resolve-external-includes",
            "--no-enrich",
        ],
    )
    assert result.exit_code == 2


def test_lock_generate_and_update_os_errors(tmp_path):
    from unittest.mock import patch

    pipeline = _pipeline(tmp_path)
    runner = CliRunner()

    with patch(
        "src.gitlab_compliance.build_lockfile",
        side_effect=OSError("boom"),
    ):
        generate = runner.invoke(
            gitlab_compliance,
            [
                "lock",
                "generate",
                "-p",
                str(pipeline),
                "-l",
                str(tmp_path / "a.lock"),
                "--no-resolve-external-includes",
                "--no-enrich",
            ],
        )
        update = runner.invoke(
            gitlab_compliance,
            [
                "lock",
                "update",
                "-p",
                str(pipeline),
                "-l",
                str(tmp_path / "b.lock"),
                "--no-resolve-external-includes",
                "--no-enrich",
            ],
        )
    assert generate.exit_code == 2
    assert update.exit_code == 2
    assert "boom" in generate.output


def test_lock_fingerprint_rejects_corrupt_lock(tmp_path):
    import json

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
            "--no-enrich",
            "--quiet",
        ],
    )
    payload = json.loads(lock_file.read_text(encoding="utf-8"))
    payload["fingerprint"] = "sha256:deadbeef"
    lock_file.write_text(json.dumps(payload), encoding="utf-8")
    result = runner.invoke(
        gitlab_compliance,
        ["lock", "fingerprint", "--from-lock", "-l", str(lock_file)],
    )
    assert result.exit_code == 2
    assert "does not match" in result.output.lower()

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
            "--no-enrich",
        ],
    )
    assert verify.exit_code == 2
    assert "does not match" in verify.output.lower()
