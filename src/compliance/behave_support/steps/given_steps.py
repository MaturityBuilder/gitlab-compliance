"""GIVEN steps for GitLab compliance policies."""

from __future__ import annotations

from behave import given

from src.compliance.api_config import require_api_connection, require_gitlab_api
from src.compliance.behave_support.environment import _skip_remaining_steps
from src.compliance.stash import (
    container_image_release_metadata_resolved,
    filter_entities,
    include_release_metadata_resolved,
)


def _set_stash(context, entities: list[dict]):
    context.stash = list(entities)
    context.step_mode = "given"
    context.scenario_skipped = False


def _set_stash_or_skip(context, entities: list[dict], *, skip_reason: str):
    if not entities:
        _skip_remaining_steps(context, skip_reason)
        return
    _set_stash(context, entities)


@given("I have any job defined")
def given_any_job(context):
    _set_stash(context, context.compliance_entities.get("jobs", []))


@given('I have job "{name}" defined')
def given_named_job(context, name):
    jobs = [
        job
        for job in context.compliance_entities.get("jobs", [])
        if job.get("name") == name
    ]
    _set_stash_or_skip(
        context, jobs, skip_reason=f'No job named "{name}" found in pipeline'
    )


@given("I have any include defined")
def given_any_include(context):
    _set_stash(context, context.compliance_entities.get("includes", []))


@given('I have include type "{include_type}" defined')
def given_include_type(context, include_type):
    includes = filter_entities(
        context.compliance_entities.get("includes", []),
        lambda entity: entity.get("include_type") == include_type,
    )
    _set_stash_or_skip(
        context,
        includes,
        skip_reason=f'No includes of type "{include_type}" found in pipeline',
    )


@given("I have any include with release metadata defined")
def given_any_include_with_release_metadata(context):
    if not require_gitlab_api(context, "include release checks"):
        return
    includes = filter_entities(
        context.compliance_entities.get("includes", []),
        include_release_metadata_resolved,
    )
    _set_stash_or_skip(
        context,
        includes,
        skip_reason="No includes with release metadata resolved",
    )


@given("I have any container image defined")
def given_any_container_image(context):
    _set_stash(context, context.compliance_entities.get("container_images", []))


@given('I have container image from "{image_source}" defined')
def given_container_image_from_source(context, image_source):
    images = filter_entities(
        context.compliance_entities.get("container_images", []),
        lambda entity: entity.get("image_source") == image_source,
    )
    _set_stash_or_skip(
        context,
        images,
        skip_reason=f'No container images from "{image_source}" found in pipeline',
    )


@given("I have any container image with release metadata defined")
def given_any_container_image_with_release_metadata(context):
    images = filter_entities(
        context.compliance_entities.get("container_images", []),
        container_image_release_metadata_resolved,
    )
    _set_stash_or_skip(
        context,
        images,
        skip_reason="No container images with release metadata resolved",
    )


@given("I have any variable defined")
def given_any_variable(context):
    _set_stash(context, context.compliance_entities.get("variables", []))


@given("I have any workflow rule defined")
def given_any_workflow_rule(context):
    _set_stash(context, context.compliance_entities.get("workflow_rules", []))


@given("I have any project setting defined")
def given_any_project_setting(context):
    if not require_api_connection(context, "project", "project setting checks"):
        return
    _set_stash(context, context.compliance_entities.get("project_settings", []))


@given('I have project setting "{name}" defined')
def given_project_setting(context, name):
    if not require_api_connection(context, "project", "project setting checks"):
        return
    settings = [
        setting
        for setting in context.compliance_entities.get("project_settings", [])
        if setting.get("name") == name
    ]
    _set_stash_or_skip(
        context,
        settings,
        skip_reason=f'No project setting "{name}" found',
    )


@given("I have any project ci variable defined")
def given_any_project_ci_variable(context):
    if not require_api_connection(context, "project", "project CI variable checks"):
        return
    _set_stash(context, context.compliance_entities.get("project_ci_variables", []))


@given("I have any group setting defined")
def given_any_group_setting(context):
    if not require_api_connection(context, "group", "group setting checks"):
        return
    _set_stash(context, context.compliance_entities.get("group_settings", []))
