"""THEN steps for GitLab compliance policies."""

from __future__ import annotations

from behave import then

from src.compliance.stash import (
    assert_all,
    entity_has_property,
    extends_includes,
    get_property,
    include_has_newer_release,
    include_has_valid_semver,
    include_newer_release_older_than_days,
    include_release_lag_exceeds_days,
    include_version_is_latest,
    include_within_latest_tags,
    container_image_has_newer_release,
    container_image_newer_release_older_than_days,
    container_image_release_lag_exceeds_days,
    container_image_uses_sha256,
    container_image_within_latest_tags,
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


@then("it must use valid semver")
def then_version_valid_semver(context):
    if not _ensure_then_mode(context):
        return
    assert_all(
        context.stash,
        include_has_valid_semver,
        "Includes must use a valid semver version",
    )


@then("a newer release must not be available")
def then_no_newer_release(context):
    if not _ensure_then_mode(context):
        return
    assert_all(
        context.stash,
        lambda e: not include_has_newer_release(e),
        "Includes must not have a newer release available",
    )


@then("a newer release must not be available for more than {days:d} days")
def then_no_newer_release_beyond_grace_days(context, days):
    if not _ensure_then_mode(context):
        return
    assert_all(
        context.stash,
        lambda e: not include_newer_release_older_than_days(e, days),
        f"Includes must not have a newer release available for more than {days} days",
    )


@then("its release lag must not exceed {days:d} days")
def then_release_lag_must_not_exceed_days(context, days):
    if not _ensure_then_mode(context):
        return
    assert_all(
        context.stash,
        lambda e: not include_release_lag_exceeds_days(e, days),
        f"Includes must not have release lag exceeding {days} days",
    )


@then("it must be within the latest {count:d} tags")
def then_must_be_within_latest_tags(context, count):
    if not _ensure_then_mode(context):
        return
    assert_all(
        context.stash,
        lambda e: include_within_latest_tags(e, count),
        f"Includes must be within the latest {count} semver tags",
    )


@then("it must use sha256 digest")
def then_must_use_sha256_digest(context):
    if not _ensure_then_mode(context):
        return
    assert_all(
        context.stash,
        container_image_uses_sha256,
        "Container images must use a sha256 digest",
    )


@then("a newer image release must not be available")
def then_no_newer_image_release(context):
    if not _ensure_then_mode(context):
        return
    assert_all(
        context.stash,
        lambda e: not container_image_has_newer_release(e),
        "Container images must not have a newer release available",
    )


@then("a newer image release must not be available for more than {days:d} days")
def then_no_newer_image_release_beyond_grace_days(context, days):
    if not _ensure_then_mode(context):
        return
    assert_all(
        context.stash,
        lambda e: not container_image_newer_release_older_than_days(e, days),
        f"Container images must not have a newer release available for more than {days} days",
    )


@then("its image release lag must not exceed {days:d} days")
def then_image_release_lag_must_not_exceed_days(context, days):
    if not _ensure_then_mode(context):
        return
    assert_all(
        context.stash,
        lambda e: not container_image_release_lag_exceeds_days(e, days),
        f"Container images must not have image release lag exceeding {days} days",
    )


@then("it must be within the latest {count:d} image tags")
def then_must_be_within_latest_image_tags(context, count):
    if not _ensure_then_mode(context):
        return
    assert_all(
        context.stash,
        lambda e: container_image_within_latest_tags(e, count),
        f"Container images must be within the latest {count} image tags",
    )


@then("it must track the latest release")
def then_version_is_latest_release(context):
    if not _ensure_then_mode(context):
        return
    assert_all(
        context.stash,
        include_version_is_latest,
        "Includes must reference the latest semver release",
    )
