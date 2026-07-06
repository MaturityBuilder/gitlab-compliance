"""GIVEN steps for GitLab compliance policies."""

from __future__ import annotations

from behave import given

from src.compliance.api_config import require_api_connection
from src.compliance.stash import filter_entities


def _set_stash(context, entities: list[dict]):
    context.stash = list(entities)
    context.step_mode = "given"
    context.scenario_skipped = False


@given("I have any job defined")
def given_any_job(context):
    _set_stash(context, context.compliance_entities.get("jobs", []))


@given('I have job "{name}" defined')
def given_named_job(context, name):
    jobs = [
        job for job in context.compliance_entities.get("jobs", [])
        if job.get("name") == name
    ]
    _set_stash(context, jobs)


@given("I have any include defined")
def given_any_include(context):
    _set_stash(context, context.compliance_entities.get("includes", []))


@given('I have include type "{include_type}" defined')
def given_include_type(context, include_type):
    includes = filter_entities(
        context.compliance_entities.get("includes", []),
        lambda entity: entity.get("include_type") == include_type,
    )
    _set_stash(context, includes)


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
        setting for setting in context.compliance_entities.get("project_settings", [])
        if setting.get("name") == name
    ]
    _set_stash(context, settings)


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
