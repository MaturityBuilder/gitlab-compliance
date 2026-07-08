"""WHEN steps for GitLab compliance policies."""

from __future__ import annotations

from behave import when

from src.compliance.behave_support.environment import _skip_remaining_steps
from src.compliance.stash import (
    container_image_has_newer_release,
    container_image_newer_release_older_than_days,
    container_image_not_within_latest_tags,
    container_image_release_lag_exceeds_days,
    entity_has_property,
    filter_entities,
    include_has_newer_release,
    include_newer_release_older_than_days,
    include_not_within_latest_tags,
    include_release_lag_exceeds_days,
    input_matches,
    name_starts_with,
    property_matches,
    property_matches_conditional,
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
    filtered = filter_entities(
        context.stash, lambda e: entity_has_property(e, property_name)
    )
    _apply_filter(context, filtered, f"No entities with property '{property_name}'")


@when("it does not have {property_name}")
def when_it_does_not_have(context, property_name):
    filtered = filter_entities(
        context.stash, lambda e: not entity_has_property(e, property_name)
    )
    _apply_filter(
        context, filtered, f"All entities already have property '{property_name}'"
    )


@when("its {property_name} is {expected}")
def when_property_is(context, property_name, expected):
    filtered = filter_entities(
        context.stash,
        lambda e: property_matches(e, property_name, expected),
    )
    _apply_filter(context, filtered, f"No entities where {property_name} is {expected}")


@when('its {property_name} matches "{pattern}"')
def when_property_matches(context, property_name, pattern):
    when_property_matches_conditional(context, property_name, pattern)


def when_property_matches_conditional(context, property_name, pattern):
    filtered = filter_entities(
        context.stash,
        lambda e: property_matches_conditional(e, property_name, pattern),
    )
    _apply_filter(
        context, filtered, f"No entities where {property_name} matches {pattern}"
    )


@when("the entity input {name} equals {value}")
def when_input_is(context, name, value):
    filtered = filter_entities(
        context.stash,
        lambda e: input_matches(e, name, value),
    )
    _apply_filter(
        context,
        filtered,
        f"No entities where input '{name}' matches '{value}'",
    )


@when("its key is {name}")
def when_key_is(context, name):
    filtered = filter_entities(
        context.stash,
        lambda e: property_matches(e, "key", name),
    )
    _apply_filter(context, filtered, f"No entities where key is {name}")


@when('its key matches "{pattern}"')
def when_key_matches(context, pattern):
    filtered = filter_entities(
        context.stash,
        lambda e: property_matches_conditional(e, "key", pattern),
    )
    _apply_filter(
        context, filtered, f"No entities where key matches {pattern}"
    )


@when('its name does not start with "{prefix}"')
def when_name_not_starts_with(context, prefix):
    filtered = filter_entities(context.stash, lambda e: not name_starts_with(e, prefix))
    _apply_filter(context, filtered, f"All entity names start with '{prefix}'")


@when("a newer release is available")
def when_newer_release_available(context):
    filtered = filter_entities(context.stash, include_has_newer_release)
    _apply_filter(context, filtered, "No includes with a newer release available")


@when("a newer release is available for more than {days:d} days")
def when_newer_release_available_for_more_than_days(context, days):
    filtered = filter_entities(
        context.stash,
        lambda e: include_newer_release_older_than_days(e, days),
    )
    _apply_filter(
        context,
        filtered,
        f"No includes with a newer release available for more than {days} days",
    )


@when("its release lag exceeds {days:d} days")
def when_release_lag_exceeds_days(context, days):
    filtered = filter_entities(
        context.stash,
        lambda e: include_release_lag_exceeds_days(e, days),
    )
    _apply_filter(
        context,
        filtered,
        f"No includes with release lag exceeding {days} days",
    )


@when("it is not within the latest {count:d} tags")
def when_not_within_latest_tags(context, count):
    filtered = filter_entities(
        context.stash,
        lambda e: include_not_within_latest_tags(e, count),
    )
    _apply_filter(
        context,
        filtered,
        f"No includes outside the latest {count} tags",
    )


@when("a newer image release is available")
def when_newer_image_release_available(context):
    filtered = filter_entities(context.stash, container_image_has_newer_release)
    _apply_filter(
        context, filtered, "No container images with a newer release available"
    )


@when("a newer image release is available for more than {days:d} days")
def when_newer_image_release_available_for_more_than_days(context, days):
    filtered = filter_entities(
        context.stash,
        lambda e: container_image_newer_release_older_than_days(e, days),
    )
    _apply_filter(
        context,
        filtered,
        f"No container images with a newer release available for more than {days} days",
    )


@when("its image release lag exceeds {days:d} days")
def when_image_release_lag_exceeds_days(context, days):
    filtered = filter_entities(
        context.stash,
        lambda e: container_image_release_lag_exceeds_days(e, days),
    )
    _apply_filter(
        context,
        filtered,
        f"No container images with image release lag exceeding {days} days",
    )


@when("it is not within the latest {count:d} image tags")
def when_not_within_latest_image_tags(context, count):
    filtered = filter_entities(
        context.stash,
        lambda e: container_image_not_within_latest_tags(e, count),
    )
    _apply_filter(
        context,
        filtered,
        f"No container images outside the latest {count} image tags",
    )
