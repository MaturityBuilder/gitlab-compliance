"""Build, verify, and fingerprint `.gitlab-ci.lock` pipeline inventories.

The lockfile is a committed inventory of the resolved CI closure — includes,
images, services, external steps, and pipeline structure — plus an optional
policy-pack hash. Teams use the fingerprint (or GitLab ``rules:changes`` on the
lock file) to skip compliance jobs when nothing inventory-relevant changed.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src import __version__
from src.compliance.image_versions import parse_container_image_ref
from src.modules.constants import DEFAULT_LOCK_FILE
from src.modules.pipeline_data import collect_pipeline_data

LOCKFILE_VERSION = 1
LOCK_GENERATOR = "gitlab-compliance"
FINGERPRINT_ENV_KEY = "GITLAB_COMPLIANCE_LOCK_FINGERPRINT"

__all__ = [
    "DEFAULT_LOCK_FILE",
    "FINGERPRINT_ENV_KEY",
    "LOCKFILE_VERSION",
    "LOCK_GENERATOR",
    "LockfileError",
    "build_inventory",
    "build_lockfile",
    "compute_fingerprint",
    "dotenv_fingerprint",
    "dumps_lockfile",
    "load_lockfile",
    "summarize_inventory",
    "verify_lockfile",
    "write_lockfile",
]


class LockfileError(ValueError):
    """Raised when a lockfile cannot be loaded or verified."""


def _sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _sha256_text(text: str) -> str:
    return _sha256_bytes(text.encode("utf-8"))


def _sha256_file(path: str | Path) -> str | None:
    file_path = Path(path)
    if not file_path.is_file():
        return None
    return _sha256_bytes(file_path.read_bytes())


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def compute_fingerprint(inventory: dict[str, Any]) -> str:
    """Return a stable fingerprint for an inventory payload."""
    return _sha256_text(_canonical_json(inventory))


def _hash_path_tree(root: str | Path) -> str | None:
    """Hash a directory of policy files (sorted paths + contents)."""
    base = Path(root)
    if not base.exists():
        return None
    if base.is_file():
        return _sha256_file(base)

    parts: list[str] = []
    for path in sorted(base.rglob("*")):
        if not path.is_file():
            continue
        if path.name.startswith(".") or "__pycache__" in path.parts:
            continue
        rel = path.relative_to(base).as_posix()
        digest = _sha256_file(path)
        if digest:
            parts.append(f"{rel}:{digest}")
    if not parts:
        return _sha256_text("")
    return _sha256_text("\n".join(parts))


def _job_attribute_map(job: dict) -> dict[str, Any]:
    values: dict[str, Any] = {}
    for attribute in job.get("attributes", []):
        values[attribute["key"]] = attribute["value"]
    if job.get("rules"):
        values["rules"] = job["rules"]
    for nested in job.get("nested", []):
        attr = nested.get("attribute")
        if attr == "variables":
            values.setdefault("variables", {})
            values["variables"][nested["key"]] = nested["value"]
        elif attr == "needs":
            values.setdefault("needs", [])
            values["needs"].append(nested["value"])
    for key in ("before_script", "script", "after_script", "effective_script"):
        if key in job:
            values[key] = job[key]
    return values


def _include_identity(include: dict) -> str:
    include_type = str(include.get("include_type", ""))
    project = str(include.get("project", ""))
    version = str(include.get("version", ""))
    file_name = str(include.get("file", ""))
    return f"{include_type}:{project}:{version}:{file_name}"


def _resolve_local_include_path(include: dict, pipeline_file: str) -> Path | None:
    """Best-effort path for a local include relative to its declaring file."""
    if include.get("include_type") != "local":
        return None
    declared = str(include.get("project", "")).strip()
    if not declared:
        return None
    source = include.get("source_file") or pipeline_file
    base_dir = Path(source).resolve().parent
    candidate = (base_dir / declared).resolve()
    if candidate.is_file():
        return candidate
    root_candidate = (Path(pipeline_file).resolve().parent / declared).resolve()
    if root_candidate.is_file():
        return root_candidate
    return None


def _include_location_key(include_type: str, source_file: str, line: int) -> str:
    return f"{include_type}|{source_file}|{line}"


def _inventory_include(
    include: dict,
    pipeline_file: str,
    *,
    unresolved_locations: set[str],
) -> dict[str, Any]:
    include_type = str(include.get("include_type", ""))
    identity = _include_identity(include)
    source_file = str(include.get("source_file", ""))
    line = int(include.get("line") or 0)
    entry: dict[str, Any] = {
        "type": include_type,
        "id": identity,
        "project": include.get("project", ""),
        "ref": include.get("version", ""),
        "file": include.get("file", ""),
        "sourceFile": source_file,
        "line": line,
        "resolved": False,
        "contentHash": None,
    }

    if include_type == "local":
        local_path = _resolve_local_include_path(include, pipeline_file)
        if local_path is not None:
            entry["resolved"] = True
            entry["contentHash"] = _sha256_file(local_path)
            entry["path"] = str(local_path)
        return entry

    location = _include_location_key(include_type, source_file, line)
    if location in unresolved_locations or include_type in {"component", "template"}:
        entry["resolved"] = False
        return entry

    # Remote/project may have been merged into the stash. Identity + ref is the
    # offline inventory pin; content hashes require fetched bodies.
    entry["resolved"] = include_type in {"remote", "project"}
    return entry


def _inventory_image(image: dict) -> dict[str, Any]:
    image_ref = str(image.get("image") or image.get("project") or "")
    parsed = parse_container_image_ref(image_ref)
    digest = parsed.get("digest") or image.get("digest") or ""
    if digest and not str(digest).startswith("sha256:"):
        digest = f"sha256:{digest}"
    latest_digest = image.get("latest_digest") or ""
    if latest_digest and not str(latest_digest).startswith("sha256:"):
        latest_digest = f"sha256:{latest_digest}"
    return {
        "source": image.get("image_source", ""),
        "parentJob": image.get("parent_job", ""),
        "image": image_ref,
        "registry": parsed.get("registry") or image.get("registry", ""),
        "repository": parsed.get("repository") or image.get("repository", ""),
        "tag": parsed.get("tag") or image.get("version", ""),
        "digest": digest,
        "resolvedDigest": latest_digest or (digest or None),
        "sourceFile": image.get("source_file", ""),
        "line": image.get("line", 0),
    }


def _inventory_external_steps(
    includes: list[dict], jobs: list[dict]
) -> list[dict[str, Any]]:
    """External steps: components, templates, and trigger jobs."""
    steps: list[dict[str, Any]] = []

    for include in includes:
        include_type = str(include.get("include_type", ""))
        if include_type not in {"component", "template"}:
            continue
        steps.append(
            {
                "kind": include_type,
                "id": _include_identity(include),
                "project": include.get("project", ""),
                "ref": include.get("version", ""),
                "sourceFile": include.get("source_file", ""),
                "line": include.get("line", 0),
            }
        )

    for job in jobs:
        values = _job_attribute_map(job)
        trigger = values.get("trigger")
        if trigger is None:
            continue
        steps.append(
            {
                "kind": "trigger",
                "id": f"trigger:{job.get('name', '')}",
                "job": job.get("name", ""),
                "trigger": trigger,
                "stage": values.get("stage", ""),
                "sourceFile": job.get("source_file", ""),
                "line": job.get("line", 0),
            }
        )

    steps.sort(key=lambda item: (item.get("kind", ""), item.get("id", "")))
    return steps


def _pipeline_inventory(
    pipeline_file: str,
    pipeline_data: dict[str, Any],
) -> dict[str, Any]:
    jobs = list(pipeline_data.get("jobs") or [])
    job_entries = []
    for job in sorted(jobs, key=lambda item: str(item.get("name", ""))):
        values = _job_attribute_map(job)
        job_entries.append(
            {
                "name": job.get("name", ""),
                "stage": values.get("stage", ""),
                "isTemplate": bool(job.get("is_template")),
                "signature": _sha256_text(_canonical_json(values)),
                "sourceFile": job.get("source_file", ""),
                "line": job.get("line", 0),
            }
        )

    variables = pipeline_data.get("variables") or []
    variable_keys = sorted(
        str(item.get("key", "")) for item in variables if item.get("key") is not None
    )
    workflow_rules = pipeline_data.get("workflow_rules") or []
    stages: list[str] = []
    # Global stages list is not first-class in pipeline_data; derive from jobs.
    seen_stages: set[str] = set()
    for job in job_entries:
        stage = str(job.get("stage") or "")
        if stage and stage not in seen_stages:
            seen_stages.add(stage)
            stages.append(stage)

    return {
        "rootFile": os.path.normpath(pipeline_file),
        "rootContentHash": _sha256_file(pipeline_file),
        "stages": stages,
        "jobs": job_entries,
        "variableKeys": variable_keys,
        "workflowRulesHash": _sha256_text(_canonical_json(workflow_rules)),
        "workflowRuleCount": len(workflow_rules),
    }


def build_inventory(
    pipeline_file: str,
    *,
    include_nested: bool = True,
    max_include_depth: int | None = None,
    resolve_external_includes: bool | None = None,
    gitlab_url: str | None = None,
    token: str | None = None,
    features_dir: str | None = None,
    enrich: bool = False,
) -> dict[str, Any]:
    """Build a lock inventory from pipeline YAML (offline by default)."""
    if not os.path.exists(pipeline_file):
        raise FileNotFoundError(f"Pipeline file not found: {pipeline_file}")

    pipeline_data = collect_pipeline_data(
        config_file=pipeline_file,
        detailed=True,
        include_nested=include_nested,
        max_include_depth=max_include_depth,
        include_scripts=True,
        resolve_job_composition=True,
        resolve_external_includes=resolve_external_includes,
        gitlab_url=gitlab_url,
        token=token,
    )

    raw_includes = list(pipeline_data.get("includes") or [])
    raw_images = list(pipeline_data.get("container_images") or [])
    unresolved = list(pipeline_data.get("unresolved_includes") or [])

    if enrich and token:
        from src.compliance.image_versions import enrich_container_images_with_releases
        from src.compliance.include_versions import enrich_includes_with_releases
        from src.compliance.release_cache import ReleaseMetadataCache

        cache = ReleaseMetadataCache()
        raw_includes = enrich_includes_with_releases(
            raw_includes,
            gitlab_url=gitlab_url,
            token=token,
            cache=cache,
        )
        raw_images = enrich_container_images_with_releases(
            raw_images,
            gitlab_url=gitlab_url,
            token=token,
            cache=cache,
        )

    unresolved_locations = {
        _include_location_key(
            str(item.get("include_type", "")),
            str(item.get("source_file", "")),
            int(item.get("line") or 0),
        )
        for item in unresolved
    }

    includes = [
        _inventory_include(
            include, pipeline_file, unresolved_locations=unresolved_locations
        )
        for include in raw_includes
    ]
    includes.sort(key=lambda item: item.get("id", ""))

    images = [_inventory_image(image) for image in raw_images]
    images.sort(
        key=lambda item: (
            item.get("source", ""),
            item.get("parentJob", ""),
            item.get("image", ""),
        )
    )

    external_steps = _inventory_external_steps(
        raw_includes, pipeline_data.get("jobs") or []
    )

    unresolved_entries = []
    for item in unresolved:
        unresolved_entries.append(
            {
                "type": item.get("include_type") or "",
                "reference": item.get("reference", ""),
                "reason": item.get("reason") or "unresolved",
                "detail": item.get("detail", ""),
                "sourceFile": item.get("source_file", ""),
                "line": item.get("line", 0),
            }
        )
    unresolved_entries.sort(
        key=lambda item: (
            item.get("type", ""),
            item.get("reference", ""),
            item.get("sourceFile", ""),
            item.get("line", 0),
        )
    )

    inventory: dict[str, Any] = {
        "pipeline": _pipeline_inventory(pipeline_file, pipeline_data),
        "includes": includes,
        "images": images,
        "externalSteps": external_steps,
        "unresolved": unresolved_entries,
    }

    if features_dir:
        policy_hash = _hash_path_tree(features_dir)
        inventory["policies"] = {
            "path": os.path.normpath(features_dir),
            "contentHash": policy_hash,
        }

    return inventory


def build_lockfile(
    pipeline_file: str,
    *,
    include_nested: bool = True,
    max_include_depth: int | None = None,
    resolve_external_includes: bool | None = None,
    gitlab_url: str | None = None,
    token: str | None = None,
    features_dir: str | None = None,
    enrich: bool = False,
) -> dict[str, Any]:
    """Build a complete lockfile document with fingerprint."""
    inventory = build_inventory(
        pipeline_file,
        include_nested=include_nested,
        max_include_depth=max_include_depth,
        resolve_external_includes=resolve_external_includes,
        gitlab_url=gitlab_url,
        token=token,
        features_dir=features_dir,
        enrich=enrich,
    )
    fingerprint = compute_fingerprint(inventory)
    return {
        "lockfileVersion": LOCKFILE_VERSION,
        "generator": LOCK_GENERATOR,
        "generatorVersion": __version__,
        "pipelineFile": os.path.normpath(pipeline_file),
        "generatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "fingerprint": fingerprint,
        "inventory": inventory,
    }


def dumps_lockfile(lockfile: dict[str, Any]) -> str:
    """Serialize a lockfile as stable, human-readable JSON."""
    return json.dumps(lockfile, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def write_lockfile(lockfile: dict[str, Any], output_file: str | Path) -> Path:
    path = Path(output_file)
    path.write_text(dumps_lockfile(lockfile), encoding="utf-8")
    return path


def load_lockfile(lock_file: str | Path) -> dict[str, Any]:
    path = Path(lock_file)
    if not path.is_file():
        raise LockfileError(f"Lock file not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise LockfileError(f"Lock file is not valid JSON: {path}") from exc
    if not isinstance(data, dict):
        raise LockfileError(f"Lock file must be a JSON object: {path}")
    if "inventory" not in data or "fingerprint" not in data:
        raise LockfileError(f"Lock file missing inventory or fingerprint: {path}")
    return data


def verify_lockfile(
    pipeline_file: str,
    lock_file: str | Path,
    *,
    include_nested: bool = True,
    max_include_depth: int | None = None,
    resolve_external_includes: bool | None = None,
    gitlab_url: str | None = None,
    token: str | None = None,
    features_dir: str | None = None,
    enrich: bool = False,
) -> dict[str, Any]:
    """Compare current inventory fingerprint to a committed lockfile.

    Returns a result dict with ``matches`` bool and fingerprint details.
    """
    existing = load_lockfile(lock_file)
    current = build_lockfile(
        pipeline_file,
        include_nested=include_nested,
        max_include_depth=max_include_depth,
        resolve_external_includes=resolve_external_includes,
        gitlab_url=gitlab_url,
        token=token,
        features_dir=features_dir,
        enrich=enrich,
    )
    expected = str(existing.get("fingerprint", ""))
    actual = str(current.get("fingerprint", ""))
    # Also accept inventory recompute from stored inventory when present.
    stored_inventory_fp = compute_fingerprint(existing.get("inventory") or {})
    matches = actual == expected or actual == stored_inventory_fp
    return {
        "matches": matches,
        "expectedFingerprint": expected,
        "actualFingerprint": actual,
        "lockFile": str(lock_file),
        "pipelineFile": pipeline_file,
        "current": current,
        "existing": existing,
    }


def dotenv_fingerprint(fingerprint: str) -> str:
    """Return a GitLab dotenv-report line for the lock fingerprint."""
    value = fingerprint.removeprefix("sha256:")
    return f"{FINGERPRINT_ENV_KEY}={value}\n"


def summarize_inventory(inventory: dict[str, Any]) -> dict[str, int]:
    """Return counts for console summaries."""
    return {
        "jobs": len((inventory.get("pipeline") or {}).get("jobs") or []),
        "includes": len(inventory.get("includes") or []),
        "images": len(inventory.get("images") or []),
        "externalSteps": len(inventory.get("externalSteps") or []),
        "unresolved": len(inventory.get("unresolved") or []),
    }
