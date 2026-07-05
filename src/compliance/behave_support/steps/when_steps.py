"""WHEN steps for GitLab compliance policies."""

from __future__ import annotations

from behave import when

from src.compliance.behave_support.environment import _skip_remaining_steps
from src.compliance.stash import (
    entity_has_property,
    filter_entities,
    name_starts_with,
    property_matches,
    property_matches_regex,
)


def _apply_filter(context, entities: list[dict], reason: str):
    if context.scenario_skipped:
        return
    context.step_mode = "when"
    if not entities:
        _skip_remaining_steps(context, reason)
        return
    context.stash = entities


@when("it has {property_name}")
def when_it_has(context, property_name):
    filtered = filter_entities(context.stash, lambda e: entity_has_property(e, property_name))
    _apply_filter(context, filtered, f"No entities with property '{property_name}'")


@when("it does not have {property_name}")
def when_it_does_not_have(context, property_name):
    filtered = filter_entities(context.stash, lambda e: not entity_has_property(e, property_name))
    _apply_filter(context, filtered, f"All entities already have property '{property_name}'")


@when("its {property_name} is {expected}")
def when_property_is(context, property_name, expected):
    filtered = filter_entities(
        context.stash,
        lambda e: property_matches(e, property_name, expected),
    )
    _apply_filter(context, filtered, f"No entities where {property_name} is {expected}")


@when('its {property_name} matches "{pattern}"')
def when_property_matches(context, property_name, pattern):
    filtered = filter_entities(
        context.stash,
        lambda e: property_matches_regex(e, property_name, pattern),
    )
    _apply_filter(context, filtered, f"No entities where {property_name} matches {pattern}")


@when('its name does not start with "{prefix}"')
def when_name_not_starts_with(context, prefix):
    filtered = filter_entities(context.stash, lambda e: not name_starts_with(e, prefix))
    _apply_filter(context, filtered, f"All entity names start with '{prefix}'")
