"""Apply supply-chain auto-fixes before compliance runs."""

from __future__ import annotations

from src.compliance.container_fix import (
    apply_container_image_fixes,
    collect_container_image_fixes,
)
from src.compliance.include_fix import (
    apply_include_version_fixes,
    collect_include_version_fixes,
)
from src.compliance.model import load_pipeline_entities
from src.compliance.release_cache import ReleaseMetadataCache
from src.compliance.secret_redact import redact_secrets
from src.modules.logging import logger


def apply_supply_chain_fixes(
    *,
    pipeline_file: str,
    include_nested: bool,
    max_include_depth: int | None = None,
    gitlab_url: str | None,
    token: str,
    project: str | None,
    group: str | None,
    cache: ReleaseMetadataCache | None = None,
) -> list[str]:
    resolved_cache = cache if cache is not None else ReleaseMetadataCache()
    entities = load_pipeline_entities(
        pipeline_file=pipeline_file,
        include_nested=include_nested,
        max_include_depth=max_include_depth,
        gitlab_url=gitlab_url,
        token=token,
        project=project,
        group=group,
        enrich_includes=True,
        enrich_images=True,
        load_api_entities=False,
        cache=resolved_cache,
    )

    messages: list[str] = []
    include_fixes = collect_include_version_fixes(entities)
    applied_includes = apply_include_version_fixes(include_fixes)
    for fix in applied_includes:
        messages.append(
            f"Fixed include {fix.project}: {fix.current_version} -> {fix.latest_version} "
            f"({fix.source_file}:{fix.line})"
        )

    if applied_includes:
        entities = load_pipeline_entities(
            pipeline_file=pipeline_file,
            include_nested=include_nested,
            max_include_depth=max_include_depth,
            gitlab_url=gitlab_url,
            token=token,
            project=project,
            group=group,
            enrich_includes=True,
            enrich_images=True,
            load_api_entities=False,
            cache=resolved_cache,
        )

    image_fixes = collect_container_image_fixes(entities)
    for fix in apply_container_image_fixes(image_fixes):
        messages.append(
            f"Fixed image {fix.current_image} -> {fix.fixed_image} "
            f"({fix.image_source} {fix.parent_job}, {fix.source_file}:{fix.line})"
        )

    for message in messages:
        logger.info(redact_secrets(message))
    return messages
