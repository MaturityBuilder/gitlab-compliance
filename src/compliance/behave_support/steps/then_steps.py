"""THEN steps for GitLab compliance policies."""

from __future__ import annotations

from behave import then

from src.compliance.stash import (
    assert_all,
    entity_has_property,
    extends_includes,
    get_property,
    normalize_value,
    property_matches,
    property_matches_regex,
    property_not_matches_regex,
)


def _ensure_then_mode(context):
    if context.scenario_skipped:
        return False
    context.step_mode = "then"
    if not context.stash:
        raise AssertionError("No entities in stash to assert against.")
    return True


@then("it must contain {property_name}")
def then_must_contain(context, property_name):
    if not _ensure_then_mode(context):
        return
    assert_all(
        context.stash,
        lambda e: entity_has_property(e, property_name),
        f"Entities missing required property '{property_name}'",
    )


@then("it must not contain {property_name}")
def then_must_not_contain(context, property_name):
    if not _ensure_then_mode(context):
        return
    assert_all(
        context.stash,
        lambda e: not entity_has_property(e, property_name),
        f"Entities must not contain '{property_name}'",
    )


@then("its {property_name} must be {expected}")
def then_property_must_be(context, property_name, expected):
    if not _ensure_then_mode(context):
        return
    assert_all(
        context.stash,
        lambda e: property_matches(e, property_name, expected),
        f"Entities where {property_name} must be {expected}",
    )


@then('its {property_name} must match "{pattern}"')
def then_property_must_match(context, property_name, pattern):
    if not _ensure_then_mode(context):
        return
    assert_all(
        context.stash,
        lambda e: property_matches_regex(e, property_name, pattern),
        f"Entities where {property_name} must match /{pattern}/",
    )


@then('its {property_name} must not match "{pattern}"')
def then_property_must_not_match(context, property_name, pattern):
    if not _ensure_then_mode(context):
        return
    assert_all(
        context.stash,
        lambda e: property_not_matches_regex(e, property_name, pattern),
        f"Entities where {property_name} must not match /{pattern}/",
    )


@then("its {property_name} must not be null")
def then_property_not_null(context, property_name):
    if not _ensure_then_mode(context):
        return
    assert_all(
        context.stash,
        lambda e: normalize_value(get_property(e, property_name)).strip() != "",
        f"Entities where {property_name} must not be null",
    )


@then('its extends must include "{template}"')
def then_extends_includes(context, template):
    if not _ensure_then_mode(context):
        return
    assert_all(
        context.stash,
        lambda e: extends_includes(e, template),
        f"Entities must extend '{template}'",
    )
