"""Unit tests for `.gitlab-ci.lock` inventory helpers."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.compliance.lockfile import (
    DEFAULT_LOCK_FILE,
    FINGERPRINT_ENV_KEY,
    LockfileError,
    build_inventory,
    build_lockfile,
    compute_fingerprint,
    dotenv_fingerprint,
    load_lockfile,
    summarize_inventory,
    verify_lockfile,
    write_lockfile,
)


def _write_pipeline(tmp_path: Path) -> Path:
    nested = tmp_path / "nested.yml"
    nested.write_text(
        "nested-job:\n  script:\n    - echo nested\n",
        encoding="utf-8",
    )
    pipeline = tmp_path / ".gitlab-ci.yml"
    pipeline.write_text(
        "\n".join(
            [
                "include:",
                "  - local: nested.yml",
                "  - component: https://gitlab.com/org/component@1.2.3",
                "stages: [build]",
                "variables:",
                "  FOO: bar",
                "build:",
                "  stage: build",
                "  image: alpine:3.19",
                "  services:",
                "    - name: postgres:16",
                "  script:",
                "    - echo hi",
                "deploy:",
                "  stage: build",
                "  trigger:",
                "    project: other/project",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return pipeline


def test_build_inventory_includes_images_services_and_external_steps(tmp_path):
    pipeline = _write_pipeline(tmp_path)
    inventory = build_inventory(
        str(pipeline), resolve_external_includes=False, enrich=False
    )

    assert inventory["pipeline"]["rootContentHash"].startswith("sha256:")
    assert any(job["name"] == "build" for job in inventory["pipeline"]["jobs"])
    assert inventory["pipeline"]["variableKeys"] == ["FOO"]

    include_types = {item["type"] for item in inventory["includes"]}
    assert "local" in include_types
    assert "component" in include_types

    local = next(item for item in inventory["includes"] if item["type"] == "local")
    assert local["resolved"] is True
    assert local["contentHash"].startswith("sha256:")

    images = {(item["source"], item["image"]) for item in inventory["images"]}
    assert ("job", "alpine:3.19") in images
    assert ("service", "postgres:16") in images

    kinds = {item["kind"] for item in inventory["externalSteps"]}
    assert "component" in kinds
    assert "trigger" in kinds

    counts = summarize_inventory(inventory)
    assert counts["images"] == 2
    assert counts["externalSteps"] >= 2


def test_build_lockfile_fingerprint_stable(tmp_path):
    pipeline = _write_pipeline(tmp_path)
    first = build_lockfile(str(pipeline), resolve_external_includes=False, enrich=False)
    second = build_lockfile(
        str(pipeline), resolve_external_includes=False, enrich=False
    )
    assert first["fingerprint"] == second["fingerprint"]
    assert first["fingerprint"] == compute_fingerprint(first["inventory"])
    assert first["lockfileVersion"] == 1
    assert first["generator"] == "gitlab-compliance"


def test_write_and_verify_lockfile(tmp_path):
    pipeline = _write_pipeline(tmp_path)
    lock_path = tmp_path / DEFAULT_LOCK_FILE
    lockfile = build_lockfile(
        str(pipeline), resolve_external_includes=False, enrich=False
    )
    write_lockfile(lockfile, lock_path)

    result = verify_lockfile(
        str(pipeline), lock_path, resolve_external_includes=False, enrich=False
    )
    assert result["matches"] is True

    pipeline.write_text(pipeline.read_text(encoding="utf-8") + "\n# drift\n")
    drifted = verify_lockfile(
        str(pipeline), lock_path, resolve_external_includes=False, enrich=False
    )
    assert drifted["matches"] is False


def test_policy_directory_changes_fingerprint(tmp_path):
    pipeline = _write_pipeline(tmp_path)
    policies = tmp_path / "policies"
    policies.mkdir()
    feature = policies / "rules.feature"
    feature.write_text("Feature: sample\n", encoding="utf-8")

    locked = build_lockfile(
        str(pipeline),
        features_dir=str(policies),
        resolve_external_includes=False,
        enrich=False,
    )
    feature.write_text("Feature: changed\n", encoding="utf-8")
    updated = build_lockfile(
        str(pipeline),
        features_dir=str(policies),
        resolve_external_includes=False,
        enrich=False,
    )
    assert locked["fingerprint"] != updated["fingerprint"]
    assert locked["inventory"]["policies"]["contentHash"].startswith("sha256:")


def test_load_lockfile_errors(tmp_path):
    missing = tmp_path / "missing.lock"
    with pytest.raises(LockfileError, match="not found"):
        load_lockfile(missing)

    bad = tmp_path / "bad.lock"
    bad.write_text("not-json", encoding="utf-8")
    with pytest.raises(LockfileError, match="not valid JSON"):
        load_lockfile(bad)

    incomplete = tmp_path / "incomplete.lock"
    incomplete.write_text(json.dumps({"lockfileVersion": 1}), encoding="utf-8")
    with pytest.raises(LockfileError, match="missing inventory"):
        load_lockfile(incomplete)


def test_dotenv_fingerprint_format():
    line = dotenv_fingerprint("sha256:abc123")
    assert line == f"{FINGERPRINT_ENV_KEY}=abc123\n"
