"""Behave environment for GitLab compliance policies."""

from __future__ import annotations

from src.compliance.model import load_pipeline_entities


def before_all(context):
    context.compliance_entities = {}
    context.stash = []
    context.step_mode = None
    context.scenario_skipped = False


def before_scenario(context, scenario):
    context.stash = []
    context.step_mode = None
    context.scenario_skipped = False

    pipeline = context.config.userdata.get("pipeline")
    if not pipeline:
        raise RuntimeError("Pipeline file not configured for compliance run.")

    if not context.compliance_entities:
        context.compliance_entities = load_pipeline_entities(
            pipeline_file=pipeline,
            include_nested=context.config.userdata.get("include_nested", "true")
            == "true",
            gitlab_url=context.config.userdata.get("gitlab_url") or None,
            project=context.config.userdata.get("project") or None,
            group=context.config.userdata.get("group") or None,
            enrich_includes=context.config.userdata.get("enrich_includes", "true")
            == "true",
            enrich_images=context.config.userdata.get("enrich_images", "true")
            == "true",
            load_api_entities=context.config.userdata.get("load_api_entities", "true")
            == "true",
        )


def _skip_remaining_steps(context, reason: str):
    context.scenario_skipped = True
    context.scenario.skip(reason)
