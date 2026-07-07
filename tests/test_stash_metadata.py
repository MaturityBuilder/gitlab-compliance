import pytest

from src.compliance.stash import (
    container_image_has_newer_release,
    container_image_newer_release_older_than_days,
    container_image_not_within_latest_tags,
    container_image_release_lag_exceeds_days,
    container_image_release_metadata_resolved,
    container_image_uses_sha256,
    container_image_within_latest_tags,
    include_newer_release_older_than_days,
    include_not_within_latest_tags,
    include_release_lag_exceeds_days,
    include_release_metadata_resolved,
    include_version_is_latest,
    include_within_latest_tags,
)


@pytest.mark.parametrize(
    ("entity", "expected"),
    [
        (
            {
                "release_metadata_resolved": True,
                "version": "1.0.0",
                "latest_version": "1.0.0",
            },
            True,
        ),
        (
            {
                "release_metadata_resolved": True,
                "version": "1.0.0",
                "latest_version": "2.0.0",
            },
            False,
        ),
        (
            {
                "release_metadata_resolved": False,
                "version": "1.0.0",
                "latest_version": "1.0.0",
            },
            False,
        ),
    ],
)
def test_include_version_is_latest(entity, expected):
    assert include_version_is_latest(entity) is expected


@pytest.mark.parametrize(
    ("entity", "expected"),
    [
        ({"release_metadata_resolved": True}, True),
        ({}, False),
    ],
)
def test_include_release_metadata_resolved(entity, expected):
    assert include_release_metadata_resolved(entity) is expected


@pytest.mark.parametrize(
    ("entity", "days", "expected"),
    [
        ({"update_available": True, "latest_release_age_days": 45}, 30, True),
        ({"update_available": True, "latest_release_age_days": 10}, 30, False),
        ({"update_available": False, "latest_release_age_days": 45}, 30, False),
        ({"update_available": True}, 30, False),
    ],
)
def test_include_newer_release_older_than_days(entity, days, expected):
    assert include_newer_release_older_than_days(entity, days) is expected


@pytest.mark.parametrize(
    ("entity", "days", "expected"),
    [
        ({"update_available": True, "release_lag_days": 120}, 90, True),
        ({"update_available": True, "release_lag_days": 30}, 90, False),
        ({"update_available": False, "release_lag_days": 120}, 90, False),
        ({"update_available": True}, 90, False),
    ],
)
def test_include_release_lag_exceeds_days(entity, days, expected):
    assert include_release_lag_exceeds_days(entity, days) is expected


@pytest.mark.parametrize(
    ("entity", "count", "expected"),
    [
        ({"release_metadata_resolved": True, "version_tag_rank": 2}, 3, True),
        ({"release_metadata_resolved": True, "version_tag_rank": 5}, 3, False),
        ({"release_metadata_resolved": True}, 3, False),
        ({"release_metadata_resolved": False, "version_tag_rank": 1}, 3, False),
    ],
)
def test_include_within_latest_tags(entity, count, expected):
    assert include_within_latest_tags(entity, count) is expected


@pytest.mark.parametrize(
    ("entity", "count", "expected"),
    [
        ({"release_metadata_resolved": True, "version_tag_rank": 5}, 3, True),
        ({"release_metadata_resolved": True, "version_tag_rank": 2}, 3, False),
        ({"release_metadata_resolved": True}, 3, True),
        ({"release_metadata_resolved": False, "version_tag_rank": 5}, 3, False),
    ],
)
def test_include_not_within_latest_tags(entity, count, expected):
    assert include_not_within_latest_tags(entity, count) is expected


@pytest.mark.parametrize(
    ("entity", "expected"),
    [
        ({"image": "python@sha256:abc123"}, True),
        ({"project": "registry.example.com/app@sha256:deadbeef"}, True),
        ({"image": "python:3.12.0"}, False),
    ],
)
def test_container_image_uses_sha256(entity, expected):
    assert container_image_uses_sha256(entity) is expected


@pytest.mark.parametrize(
    ("entity", "expected"),
    [
        ({"update_available": True}, True),
        ({"update_available": False}, False),
    ],
)
def test_container_image_has_newer_release(entity, expected):
    assert container_image_has_newer_release(entity) is expected


@pytest.mark.parametrize(
    ("entity", "expected"),
    [
        ({"release_metadata_resolved": True}, True),
        ({}, False),
    ],
)
def test_container_image_release_metadata_resolved(entity, expected):
    assert container_image_release_metadata_resolved(entity) is expected


@pytest.mark.parametrize(
    ("entity", "days", "expected"),
    [
        ({"update_available": True, "latest_release_age_days": 45}, 30, True),
        ({"update_available": True, "latest_release_age_days": 10}, 30, False),
        ({"update_available": False, "latest_release_age_days": 45}, 30, False),
        ({"update_available": True}, 30, False),
    ],
)
def test_container_image_newer_release_older_than_days(entity, days, expected):
    assert container_image_newer_release_older_than_days(entity, days) is expected


@pytest.mark.parametrize(
    ("entity", "days", "expected"),
    [
        ({"update_available": True, "release_lag_days": 120}, 90, True),
        ({"update_available": True, "release_lag_days": 30}, 90, False),
        ({"update_available": False, "release_lag_days": 120}, 90, False),
        ({"update_available": True}, 90, False),
    ],
)
def test_container_image_release_lag_exceeds_days(entity, days, expected):
    assert container_image_release_lag_exceeds_days(entity, days) is expected


@pytest.mark.parametrize(
    ("entity", "count", "expected"),
    [
        ({"release_metadata_resolved": True, "version_tag_rank": 2}, 3, True),
        ({"release_metadata_resolved": True, "version_tag_rank": 5}, 3, False),
        ({"release_metadata_resolved": True}, 3, False),
        ({"release_metadata_resolved": False, "version_tag_rank": 1}, 3, False),
    ],
)
def test_container_image_within_latest_tags(entity, count, expected):
    assert container_image_within_latest_tags(entity, count) is expected


@pytest.mark.parametrize(
    ("entity", "count", "expected"),
    [
        ({"release_metadata_resolved": True, "version_tag_rank": 5}, 3, True),
        ({"release_metadata_resolved": True, "version_tag_rank": 2}, 3, False),
        ({"release_metadata_resolved": True}, 3, True),
        ({"release_metadata_resolved": False, "version_tag_rank": 5}, 3, False),
    ],
)
def test_container_image_not_within_latest_tags(entity, count, expected):
    assert container_image_not_within_latest_tags(entity, count) is expected
