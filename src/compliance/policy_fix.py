"""Allowlisted BDD policy remediations for ``--fix-policies``.

Only explicitly documented policy IDs are remediable. Everything else is left
untouched and reported as not auto-fixable.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from src.compliance.console import print_info, print_warning
from src.compliance.container_fix import (
    apply_container_image_fixes,
    collect_container_image_fixes,
)
from src.compliance.include_fix import (
    apply_include_version_fixes,
    collect_include_version_fixes,
)
from src.compliance.model import load_pipeline_entities
from src.compliance.models import ScenarioResult
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
                "GLCI-INCLUDE-VERSIONS-003",
                "GLCI-INCLUDE-VERSIONS-004",
                "GLCI-INCLUDE-VERSIONS-005",
                "GLCI-INCLUDE-VERSIONS-006",
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
        policy_ids=frozenset({"GLCI-IMAGE-PINNING-001"}),
        title="Pin container images to sha256 digests",
        description=(
            "When a job or service image is not digest-pinned, rewrite the image "
            "reference to `@sha256:<digest>` for the currently resolved tag."
        ),
        kind="image_digest",
    ),
)

_POLICY_ID_TO_KIND: dict[str, str] = {
    policy_id: remediation.kind
    for remediation in SUPPORTED_REMEDIATIONS
    for policy_id in remediation.policy_ids
}


def supported_policy_ids() -> frozenset[str]:
    return frozenset(_POLICY_ID_TO_KIND)


def remediation_kind_for_policy(policy_id: str) -> str | None:
    return _POLICY_ID_TO_KIND.get(policy_id)


def _apply_include_latest(
    *,
    pipeline_file: str,
    include_nested: bool,
    max_include_depth: int | None,
    gitlab_url: str | None,
    token: str,
    project: str | None,
    group: str | None,
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
    )
    messages: list[str] = []
    for fix in apply_include_version_fixes(collect_include_version_fixes(entities)):
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
    )
    messages: list[str] = []
    for fix in apply_container_image_fixes(collect_container_image_fixes(entities)):
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
    unsupported: list[ScenarioResult] = []
    for scenario in failed:
        kind = remediation_kind_for_policy(scenario.policy_id)
        if kind is None:
            unsupported.append(scenario)
        else:
            kinds.add(kind)

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
    }
    # Includes first so image enrichment sees updated files when both apply.
    for kind in ("include_latest", "image_digest"):
        if kind not in kinds:
            continue
        applied = _KIND_APPLIERS[kind](**apply_kwargs)
        messages.extend(applied)

    for message in messages:
        logger.info(message)
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
