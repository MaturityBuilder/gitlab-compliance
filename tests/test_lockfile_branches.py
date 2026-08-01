"""Branch-complete unit tests for ``src.compliance.lockfile`` helpers."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from src.compliance.lockfile import (
    LockfileError,
    _hash_path_tree,
    _inventory_external_steps,
    _inventory_image,
    _inventory_include,
    _job_attribute_map,
    _normalize_digest,
    _portable_path,
    _resolve_local_include_path,
    _sha256_file,
    build_inventory,
    build_lockfile,
    dumps_lockfile,
    load_lockfile,
    verify_lockfile,
    write_lockfile,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "lock"
FULL = FIXTURES / "full-inventory" / ".gitlab-ci.yml"
MINIMAL = FIXTURES / "minimal" / ".gitlab-ci.yml"
POLICIES = FIXTURES / "policies"


def test_sha256_file_missing_returns_none(tmp_path):
    assert _sha256_file(tmp_path / "missing.txt") is None


def test_portable_path_and_normalize_digest(tmp_path):
    pipeline = tmp_path / ".gitlab-ci.yml"
    pipeline.write_text("job:\n  script: [x]\n", encoding="utf-8")
    assert _portable_path("", str(pipeline)) == ""
    assert _portable_path(pipeline, str(pipeline)) == ".gitlab-ci.yml"
    # Absolute path outside pipeline root → basename only.
    outside = Path("/tmp/foreign-lock-path.yml")
    assert _portable_path(outside, str(pipeline)) == "foreign-lock-path.yml"
    # Relative path that cannot resolve under root stays relative-ish.
    assert _portable_path("nested/file.yml", str(pipeline)) in {
        "nested/file.yml",
        "file.yml",
    }

    assert _normalize_digest("") == ""
    assert _normalize_digest("sha256:abc") == "sha256:abc"
    assert _normalize_digest("abc") == "sha256:abc"


def test_hash_path_tree_missing_file_and_empty_dir(tmp_path):
    assert _hash_path_tree(tmp_path / "nope") is None

    empty = tmp_path / "empty"
    empty.mkdir()
    # Only hidden / pycache skipped → empty parts hash.
    (empty / ".secret").write_text("x", encoding="utf-8")
    pycache = empty / "__pycache__"
    pycache.mkdir()
    (pycache / "mod.pyc").write_text("bin", encoding="utf-8")
    nested_dir = empty / "subdir"
    nested_dir.mkdir()
    digest = _hash_path_tree(empty)
    assert digest and digest.startswith("sha256:")

    single = tmp_path / "one.feature"
    single.write_text("Feature: x\n", encoding="utf-8")
    assert _hash_path_tree(single) == _sha256_file(single)


def test_job_attribute_map_rules_variables_needs_scripts():
    job = {
        "attributes": [{"key": "stage", "value": "build"}],
        "rules": [{"if": "$CI_COMMIT_TAG"}],
        "nested": [
            {"attribute": "variables", "key": "FOO", "value": "1"},
            {"attribute": "needs", "key": "", "value": "lint"},
            {"attribute": "other", "key": "x", "value": "y"},
        ],
        "before_script": ["echo a"],
        "script": ["echo b"],
        "after_script": ["echo c"],
        "effective_script": ["echo a", "echo b"],
    }
    values = _job_attribute_map(job)
    assert values["stage"] == "build"
    assert values["rules"] == [{"if": "$CI_COMMIT_TAG"}]
    assert values["variables"] == {"FOO": "1"}
    assert values["needs"] == ["lint"]
    assert values["before_script"] == ["echo a"]
    assert values["effective_script"] == ["echo a", "echo b"]


def test_resolve_local_include_path_branches(tmp_path):
    root = tmp_path / "root.yml"
    root.write_text("job:\n  script: [x]\n", encoding="utf-8")
    nested_dir = tmp_path / "nested"
    nested_dir.mkdir()
    target = tmp_path / "shared.yml"
    target.write_text("x:\n  script: [y]\n", encoding="utf-8")
    nested_local = nested_dir / "child.yml"
    nested_local.write_text("x:\n  script: [y]\n", encoding="utf-8")

    assert _resolve_local_include_path({"include_type": "project"}, str(root)) is None
    assert (
        _resolve_local_include_path(
            {"include_type": "local", "project": "  "}, str(root)
        )
        is None
    )

    # Contained relative to declaring nested file.
    found_nested = _resolve_local_include_path(
        {
            "include_type": "local",
            "project": "child.yml",
            "source_file": str(nested_local),
        },
        str(root),
    )
    assert found_nested == nested_local.resolve()

    # Fallback to pipeline-root containment.
    found_root = _resolve_local_include_path(
        {
            "include_type": "local",
            "project": "shared.yml",
            "source_file": str(nested_local),
        },
        str(root),
    )
    assert found_root == target.resolve()

    # Path escape rejected.
    outside = tmp_path.parent / "outside-lock-secret.env"
    assert (
        _resolve_local_include_path(
            {
                "include_type": "local",
                "project": "../outside-lock-secret.env",
                "source_file": str(root),
            },
            str(root),
        )
        is None
    )

    missing = _resolve_local_include_path(
        {
            "include_type": "local",
            "project": "absent.yml",
            "source_file": str(nested_local),
        },
        str(root),
    )
    assert missing is None
    del outside


def test_inventory_include_remote_project_template_and_unresolved(tmp_path):
    pipeline = tmp_path / ".gitlab-ci.yml"
    pipeline.write_text("job:\n  script: [x]\n", encoding="utf-8")
    local = tmp_path / "ok.yml"
    local.write_text("a:\n  script: [x]\n", encoding="utf-8")

    resolved_local = _inventory_include(
        {
            "include_type": "local",
            "project": "ok.yml",
            "version": "n/a",
            "source_file": str(pipeline),
            "line": 1,
        },
        str(pipeline),
        unresolved_locations=set(),
    )
    assert resolved_local["resolved"] is True
    assert resolved_local["contentHash"]

    pending_local = _inventory_include(
        {
            "include_type": "local",
            "project": "missing.yml",
            "version": "n/a",
            "source_file": str(pipeline),
            "line": 2,
        },
        str(pipeline),
        unresolved_locations=set(),
    )
    assert pending_local["resolved"] is False

    remote = _inventory_include(
        {
            "include_type": "remote",
            "project": "https://example.com/a.yml",
            "version": "1.0.0",
            "source_file": str(pipeline),
            "line": 3,
        },
        str(pipeline),
        unresolved_locations=set(),
    )
    assert remote["resolved"] is True

    project = _inventory_include(
        {
            "include_type": "project",
            "project": "group/proj",
            "version": "1.0.0",
            "file": "ci.yml",
            "source_file": str(pipeline),
            "line": 4,
        },
        str(pipeline),
        unresolved_locations=set(),
    )
    assert project["resolved"] is True

    unresolved_project = _inventory_include(
        {
            "include_type": "project",
            "project": "group/proj",
            "version": "1.0.0",
            "file": "ci.yml",
            "source_file": str(pipeline),
            "line": 5,
        },
        str(pipeline),
        unresolved_locations={f"project|{pipeline}|5"},
    )
    assert unresolved_project["resolved"] is False

    template = _inventory_include(
        {
            "include_type": "template",
            "project": "Auto-DevOps.gitlab-ci.yml",
            "version": "n/a",
            "source_file": str(pipeline),
            "line": 6,
        },
        str(pipeline),
        unresolved_locations=set(),
    )
    assert template["resolved"] is False
    assert template["id"].startswith("template:")


def test_inventory_image_digest_normalization():
    with_prefix = _inventory_image(
        {
            "image": "alpine@sha256:abc",
            "image_source": "job",
            "parent_job": "build",
            "latest_digest": "deadbeef",
        },
        ".gitlab-ci.yml",
    )
    assert with_prefix["digest"] == "sha256:abc"
    assert with_prefix["resolvedDigest"] == "sha256:deadbeef"
    assert isinstance(with_prefix["resolvedDigest"], str)

    from_fields = _inventory_image(
        {
            "project": "python:3.12",
            "digest": "feedface",
            "image_source": "service",
            "parent_job": "build",
            "registry": "registry-1.docker.io",
            "repository": "library/python",
            "version": "3.12",
        },
        ".gitlab-ci.yml",
    )
    assert from_fields["image"] == "python:3.12"
    assert from_fields["digest"] == "sha256:feedface"
    assert from_fields["resolvedDigest"] == "sha256:feedface"


def test_inventory_external_steps_template_and_trigger():
    includes = [
        {
            "include_type": "local",
            "project": "a.yml",
            "version": "n/a",
        },
        {
            "include_type": "template",
            "project": "Auto-DevOps.gitlab-ci.yml",
            "version": "n/a",
            "source_file": "ci.yml",
            "line": 1,
        },
        {
            "include_type": "component",
            "project": "https://gitlab.com/org/c",
            "version": "1.0.0",
        },
    ]
    jobs = [
        {
            "name": "plain",
            "attributes": [{"key": "stage", "value": "test"}],
        },
        {
            "name": "deploy",
            "attributes": [
                {"key": "stage", "value": "deploy"},
                {"key": "trigger", "value": {"project": "x/y"}},
            ],
            "source_file": "ci.yml",
            "line": 10,
        },
    ]
    steps = _inventory_external_steps(includes, jobs, ".gitlab-ci.yml")
    kinds = {step["kind"] for step in steps}
    assert kinds == {"component", "template", "trigger"}


def test_build_inventory_enrich_branch_mocked():
    with (
        patch(
            "src.compliance.include_versions.enrich_includes_with_releases",
            side_effect=lambda items, **kwargs: items,
        ) as include_enrich,
        patch(
            "src.compliance.image_versions.enrich_container_images_with_releases",
            side_effect=lambda items, **kwargs: items,
        ) as image_enrich,
    ):
        inventory = build_inventory(
            str(FULL),
            resolve_external_includes=False,
            enrich=True,
            token="token",
            features_dir=str(POLICIES),
        )
    assert include_enrich.called
    assert image_enrich.called
    assert inventory["policies"]["contentHash"].startswith("sha256:")
    assert any(item["type"] == "remote" for item in inventory["includes"])
    assert any(item["kind"] == "trigger" for item in inventory["externalSteps"])


def test_load_lockfile_rejects_non_object(tmp_path):
    path = tmp_path / "list.lock"
    path.write_text(json.dumps([1, 2, 3]), encoding="utf-8")
    with pytest.raises(LockfileError, match="JSON object"):
        load_lockfile(path)


def test_verify_rejects_corrupt_top_level_fingerprint(tmp_path):
    lockfile = build_lockfile(str(MINIMAL), resolve_external_includes=False)
    lockfile["fingerprint"] = "sha256:deadbeef"
    path = tmp_path / ".gitlab-ci.lock"
    write_lockfile(lockfile, path)
    result = verify_lockfile(str(MINIMAL), path, resolve_external_includes=False)
    assert result["matches"] is False
    assert result["lockIntact"] is False


def test_fingerprint_is_portable_across_directories(tmp_path):
    import shutil

    src = FIXTURES / "full-inventory"
    fps = []
    for name in ("a", "b"):
        dest = tmp_path / name
        shutil.copytree(src, dest)
        fps.append(
            build_lockfile(
                str(dest / ".gitlab-ci.yml"), resolve_external_includes=False
            )["fingerprint"]
        )
    assert fps[0] == fps[1]


def test_path_rejected_local_include_is_not_hashed(tmp_path):
    secret = tmp_path / "secret.env"
    secret.write_text("TOKEN=1\n", encoding="utf-8")
    nested = tmp_path / "ci"
    nested.mkdir()
    pipeline = nested / ".gitlab-ci.yml"
    pipeline.write_text(
        "include:\n  - local: ../secret.env\njob:\n  script: [echo]\n",
        encoding="utf-8",
    )
    inventory = build_inventory(str(pipeline), resolve_external_includes=False)
    local = next(item for item in inventory["includes"] if item["type"] == "local")
    assert local["resolved"] is False
    assert not local.get("contentHash")
    assert not str(local.get("path") or "").startswith("/")


def test_dumps_lockfile_trailing_newline():
    lockfile = build_lockfile(str(MINIMAL), resolve_external_includes=False)
    text = dumps_lockfile(lockfile)
    assert text.endswith("\n")
    assert json.loads(text)["lockfileVersion"] == 1


def test_build_inventory_missing_pipeline():
    with pytest.raises(FileNotFoundError):
        build_inventory("/tmp/does-not-exist-lock.yml")
