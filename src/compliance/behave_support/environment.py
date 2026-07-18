"""Behave environment for GitLab compliance policies."""

from __future__ import annotations

from src.compliance.model import load_pipeline_entities
from src.compliance.release_cache import ReleaseMetadataCache


def before_all(context):
    context.compliance_entities = {}
    context.stash = []
    context.step_mode = None
    context.scenario_skipped = False
    context.release_cache = context.config.userdata.get("release_cache")
    if context.release_cache is None:
        context.release_cache = ReleaseMetadataCache()


def before_scenario(context, scenario):
    context.stash = []
    context.step_mode = None
    context.scenario_skipped = False

    pipeline = context.config.userdata.get("pipeline")
    if not pipeline:
        raise RuntimeError("Pipeline file not configured for compliance run.")

    if not context.compliance_entities:
        depth_raw = context.config.userdata.get("max_include_depth", "")
        max_include_depth = int(depth_raw) if str(depth_raw).strip() else None
        context.compliance_entities = load_pipeline_entities(
            pipeline_file=pipeline,
            include_nested=context.config.userdata.get("include_nested", "true")
            == "true",
            max_include_depth=max_include_depth,
            gitlab_url=context.config.userdata.get("gitlab_url") or None,
            project=context.config.userdata.get("project") or None,
            group=context.config.userdata.get("group") or None,
            enrich_includes=context.config.userdata.get("enrich_includes", "true")
            == "true",
            enrich_images=context.config.userdata.get("enrich_images", "true")
            == "true",
            load_api_entities=context.config.userdata.get("load_api_entities", "true")
            == "true",
            cache=getattr(context, "release_cache", None),
        )


def _skip_remaining_steps(context, reason: str):
    context.scenario_skipped = True
    context.scenario.skip(reason)
