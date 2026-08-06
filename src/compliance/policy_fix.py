"""Allowlisted BDD policy remediations for ``--fix-policies``.

Only explicitly documented policy IDs are remediable. Everything else is left
untouched and reported as not auto-fixable.

Remediations apply only to entities that fail the matching policy predicates —
not every include/image in the pipeline.
"""

from __future__ import annotations

import os
from collections.abc import Callable
from dataclasses import dataclass

from src.compliance.console import print_info, print_warning
from src.compliance.container_fix import (
    ContainerImageFix,
    apply_container_image_fixes,
    collect_container_image_fixes,
)
from src.compliance.include_fix import (
    IncludeVersionFix,
    apply_include_version_fixes,
    collect_include_version_fixes,
)
from src.compliance.model import load_pipeline_entities
from src.compliance.models import ScenarioResult
from src.compliance.release_cache import ReleaseMetadataCache
from src.compliance.secret_redact import redact_secrets
from src.compliance.stash import (
    container_image_uses_sha256,
    include_has_newer_release,
    include_newer_release_older_than_days,
    include_not_within_latest_tags,
    include_release_lag_exceeds_days,
)
from src.modules.logging import logger


@dataclass(frozen=True)
class PolicyRemediation:
    """A documented, allowlisted remediation for one or more policy IDs."""

    policy_ids: frozenset[str]
    title: str
    description: str
    kind: str  # "include_latest" | "image_digest"


# Only these policy IDs are auto-fixable. Keep in sync with docs/usage/fix-policies.md.
SUPPORTED_REMEDIATIONS: tuple[PolicyRemediation, ...] = (
    PolicyRemediation(
        policy_ids=frozenset(
            {
                "GLCI-BUILTIN-INCLUDE-03",
                "GLCI-BUILTIN-INCLUDE-04",
                "GLCI-BUILTIN-INCLUDE-05",
                "GLCI-BUILTIN-INCLUDE-06",
            }
        ),
        title="Bump includes to latest semver release",
        description=(
            "When an include lags behind the latest GitLab release (or exceeds "
            "age/tag-window policies), rewrite `ref:` / `@version` to the latest "
            "semver tag discovered via the GitLab API."
        ),
        kind="include_latest",
    ),
    PolicyRemediation(
        policy_ids=frozenset({"GLCI-BUILTIN-IMAGE-01"}),
        title="Pin job container images to sha256 digests",
        description=(
            "When a job image is not digest-pinned (GLCI-BUILTIN-IMAGE-01), rewrite "
            "that image reference to `@sha256:<digest>` for the currently resolved tag. "
            "Service images are not rewritten unless they also fail an allowlisted policy."
        ),
        kind="image_digest",
    ),
)

_POLICY_ID_TO_KIND: dict[str, str] = {
    policy_id: remediation.kind
    for remediation in SUPPORTED_REMEDIATIONS
    for policy_id in remediation.policy_ids
}

# Predicates mirror the example policy Then steps (days/tag windows included).
_INCLUDE_FAIL_PREDICATES: dict[str, Callable[[dict], bool]] = {
    "GLCI-BUILTIN-INCLUDE-03": include_has_newer_release,
    "GLCI-BUILTIN-INCLUDE-04": lambda e: include_newer_release_older_than_days(e, 30),
    "GLCI-BUILTIN-INCLUDE-05": lambda e: include_release_lag_exceeds_days(e, 90),
    "GLCI-BUILTIN-INCLUDE-06": lambda e: include_not_within_latest_tags(e, 3),
}

# GLCI-BUILTIN-IMAGE-01 example policy scopes to job images only.
_IMAGE_FAIL_PREDICATES: dict[str, Callable[[dict], bool]] = {
    "GLCI-BUILTIN-IMAGE-01": lambda e: (
        str(e.get("image_source", "")) == "job" and not container_image_uses_sha256(e)
    ),
}


def supported_policy_ids() -> frozenset[str]:
    return frozenset(_POLICY_ID_TO_KIND)


def remediation_kind_for_policy(policy_id: str) -> str | None:
    return _POLICY_ID_TO_KIND.get(policy_id)


def _normalized_path(path: str) -> str:
    if not path:
        return ""
    try:
        return os.path.realpath(os.path.abspath(path))
    except OSError:
        return os.path.normpath(path)


def _entity_location(entity: dict) -> tuple[str, int]:
    return (
        _normalized_path(str(entity.get("source_file", ""))),
        int(entity.get("line", 0) or 0),
    )


def _locations_for_failed_policies(
    entities: list[dict],
    failed_policy_ids: set[str],
    predicates: dict[str, Callable[[dict], bool]],
) -> set[tuple[str, int]]:
    """Locations of entities that fail any of the given allowlisted policies."""
    active = [
        predicates[policy_id]
        for policy_id in failed_policy_ids
        if policy_id in predicates
    ]
    if not active:
        return set()
    locations: set[tuple[str, int]] = set()
    for entity in entities:
        if any(predicate(entity) for predicate in active):
            locations.add(_entity_location(entity))
    return locations


def _filter_include_fixes(
    fixes: list[IncludeVersionFix],
    locations: set[tuple[str, int]],
) -> list[IncludeVersionFix]:
    if not locations:
        return []
    return [
        fix
        for fix in fixes
        if (_normalized_path(fix.source_file), int(fix.line or 0)) in locations
    ]


def _filter_image_fixes(
    fixes: list[ContainerImageFix],
    locations: set[tuple[str, int]],
) -> list[ContainerImageFix]:
    if not locations:
        return []
    return [
        fix
        for fix in fixes
        if (_normalized_path(fix.source_file), int(fix.line or 0)) in locations
    ]


def _apply_include_latest(
    *,
    pipeline_file: str,
    include_nested: bool,
    max_include_depth: int | None,
    gitlab_url: str | None,
    token: str,
    project: str | None,
    group: str | None,
    failed_policy_ids: set[str],
    cache: ReleaseMetadataCache | None = None,
) -> list[str]:
    entities = load_pipeline_entities(
        pipeline_file=pipeline_file,
        include_nested=include_nested,
        max_include_depth=max_include_depth,
        gitlab_url=gitlab_url,
        token=token,
        project=project,
        group=group,
        enrich_includes=True,
        enrich_images=False,
        load_api_entities=False,
        cache=cache,
    )
    locations = _locations_for_failed_policies(
        entities.get("includes", []),
        failed_policy_ids,
        _INCLUDE_FAIL_PREDICATES,
    )
    candidates = _filter_include_fixes(
        collect_include_version_fixes(entities), locations
    )
    messages: list[str] = []
    for fix in apply_include_version_fixes(candidates):
        messages.append(
            f"Fixed include {fix.project}: {fix.current_version} -> {fix.latest_version} "
            f"({fix.source_file}:{fix.line})"
        )
    return messages


def _apply_image_digest(
    *,
    pipeline_file: str,
    include_nested: bool,
    max_include_depth: int | None,
    gitlab_url: str | None,
    token: str,
    project: str | None,
    group: str | None,
    failed_policy_ids: set[str],
    cache: ReleaseMetadataCache | None = None,
) -> list[str]:
    entities = load_pipeline_entities(
        pipeline_file=pipeline_file,
        include_nested=include_nested,
        max_include_depth=max_include_depth,
        gitlab_url=gitlab_url,
        token=token,
        project=project,
        group=group,
        enrich_includes=False,
        enrich_images=True,
        load_api_entities=False,
        cache=cache,
    )
    locations = _locations_for_failed_policies(
        entities.get("container_images", []),
        failed_policy_ids,
        _IMAGE_FAIL_PREDICATES,
    )
    candidates = _filter_image_fixes(collect_container_image_fixes(entities), locations)
    messages: list[str] = []
    for fix in apply_container_image_fixes(candidates):
        messages.append(
            f"Fixed image {fix.current_image} -> {fix.fixed_image} "
            f"({fix.image_source} {fix.parent_job}, {fix.source_file}:{fix.line})"
        )
    return messages


_KIND_APPLIERS: dict[str, Callable[..., list[str]]] = {
    "include_latest": _apply_include_latest,
    "image_digest": _apply_image_digest,
}


def apply_policy_remediations(
    scenario_results: list[ScenarioResult],
    *,
    pipeline_file: str,
    include_nested: bool = True,
    max_include_depth: int | None = None,
    gitlab_url: str | None = None,
    token: str = "",
    project: str | None = None,
    group: str | None = None,
    cache: ReleaseMetadataCache | None = None,
) -> list[str]:
    """Apply allowlisted remediations for failed scenarios. Returns fix messages."""
    failed = [item for item in scenario_results if item.status == "failed"]
    if not failed:
        print_info(
            "No failed policies to remediate; skipping --fix-policies.",
            title="Policy fix skipped",
        )
        return []

    kinds: set[str] = set()
    failed_policy_ids: set[str] = set()
    unsupported: list[ScenarioResult] = []
    for scenario in failed:
        kind = remediation_kind_for_policy(scenario.policy_id)
        if kind is None:
            unsupported.append(scenario)
        else:
            kinds.add(kind)
            if scenario.policy_id:
                failed_policy_ids.add(scenario.policy_id)

    for scenario in unsupported:
        label = scenario.policy_id or scenario.name
        print_warning(
            f"Policy `{label}` failed but is not auto-fixable with --fix-policies.",
            title="Not auto-fixable",
        )

    if not kinds:
        print_info(
            "Failed policies are outside the --fix-policies allowlist; no YAML changes.",
            title="Policy fix skipped",
        )
        return []

    messages: list[str] = []
    apply_kwargs = {
        "pipeline_file": pipeline_file,
        "include_nested": include_nested,
        "max_include_depth": max_include_depth,
        "gitlab_url": gitlab_url,
        "token": token,
        "project": project,
        "group": group,
        "failed_policy_ids": failed_policy_ids,
        "cache": cache,
    }
    # Includes first so image enrichment sees updated files when both apply.
    for kind in ("include_latest", "image_digest"):
        if kind not in kinds:
            continue
        applied = _KIND_APPLIERS[kind](**apply_kwargs)
        messages.extend(applied)

    for message in messages:
        logger.info(redact_secrets(message))
    if messages:
        print_info(
            f"Applied {len(messages)} policy remediation(s).",
            title="Policy fixes",
        )
    else:
        print_warning(
            "Allowlisted policies failed, but no YAML remediations could be applied "
            "(missing enrichment data or already fixed).",
            title="Policy fix",
        )
    return messages
