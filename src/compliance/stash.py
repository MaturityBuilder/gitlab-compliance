"""Entity stash helpers for compliance scenarios."""

from __future__ import annotations

import os
import re
from typing import Any, Callable


def normalize_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, (list, dict)):
        return str(value)
    return str(value)


def get_property(entity: dict, property_name: str) -> Any:
    if property_name in entity and property_name not in ("values", "type", "address"):
        return entity[property_name]

    values = entity.get("values", {})
    if not isinstance(values, dict):
        return None

    value = values.get(property_name)
    if property_name == "image" and isinstance(value, dict):
        return value.get("name", str(value))
    return value


def entity_has_property(entity: dict, property_name: str) -> bool:
    value = get_property(entity, property_name)
    if value is None:
        return False
    if isinstance(value, (list, dict)):
        return len(value) > 0
    return str(value).strip() != ""


def property_matches(entity: dict, property_name: str, expected: str) -> bool:
    return normalize_value(get_property(entity, property_name)) == expected


def _unwrap_slash_regex(spec: str) -> str:
    if len(spec) >= 2 and spec.startswith("/") and spec.endswith("/"):
        return spec[1:-1]
    return spec


def _looks_like_regex_spec(spec: str) -> bool:
    stripped = spec.strip()
    if stripped.startswith("^") or stripped.endswith("$"):
        return True
    if "|" in stripped:
        return True
    if _unwrap_slash_regex(stripped) != stripped:
        return True
    return bool(re.search(r"[.+*?\[\]()]", stripped))


def match_value_spec(actual: Any, spec: str) -> bool:
    """Match actual value against literal, comma-separated list, or regex spec."""
    actual_norm = normalize_value(actual)
    spec = spec.strip()
    if not spec:
        return actual_norm == ""

    if "," in spec and not _looks_like_regex_spec(spec):
        options = [part.strip() for part in spec.split(",") if part.strip()]
        return actual_norm in options

    if _looks_like_regex_spec(spec):
        try:
            return re.search(_unwrap_slash_regex(spec), actual_norm) is not None
        except re.error as exc:
            raise ValueError(f"Invalid regex pattern: {spec}") from exc

    return actual_norm == spec


def property_matches_spec(entity: dict, property_name: str, spec: str) -> bool:
    return match_value_spec(get_property(entity, property_name), spec)


def property_matches_regex(entity: dict, property_name: str, pattern: str) -> bool:
    return property_matches_spec(entity, property_name, pattern)


def property_not_matches_regex(entity: dict, property_name: str, pattern: str) -> bool:
    return not property_matches_regex(entity, property_name, pattern)


def name_starts_with(entity: dict, prefix: str) -> bool:
    name = entity.get("name", "")
    return str(name).startswith(prefix)


def extends_includes(entity: dict, template: str) -> bool:
    extends = get_property(entity, "extends")
    if isinstance(extends, str):
        return extends == template
    if isinstance(extends, list):
        return template in extends
    return False


def include_has_valid_semver(entity: dict) -> bool:
    return bool(entity.get("valid_version"))


def include_has_newer_release(entity: dict) -> bool:
    return bool(entity.get("update_available"))


def include_version_is_latest(entity: dict) -> bool:
    if not entity.get("release_metadata_resolved"):
        return False
    version = normalize_value(entity.get("version", ""))
    latest = normalize_value(entity.get("latest_version", ""))
    return bool(version and latest and version == latest)


def include_release_metadata_resolved(entity: dict) -> bool:
    return bool(entity.get("release_metadata_resolved"))


def include_newer_release_older_than_days(entity: dict, days: int) -> bool:
    if not entity.get("update_available"):
        return False
    age_days = entity.get("latest_release_age_days")
    if age_days is None:
        return False
    return int(age_days) > days


def include_release_lag_exceeds_days(entity: dict, days: int) -> bool:
    if not entity.get("update_available"):
        return False
    lag_days = entity.get("release_lag_days")
    if lag_days is None:
        return False
    return int(lag_days) > days


def include_within_latest_tags(entity: dict, count: int) -> bool:
    if not entity.get("release_metadata_resolved"):
        return False
    rank = entity.get("version_tag_rank")
    if rank is None:
        return False
    return int(rank) <= count


def include_not_within_latest_tags(entity: dict, count: int) -> bool:
    if not entity.get("release_metadata_resolved"):
        return False
    rank = entity.get("version_tag_rank")
    if rank is None:
        return True
    return int(rank) > count


def container_image_uses_sha256(entity: dict) -> bool:
    image = str(entity.get("image", entity.get("project", "")))
    return "@sha256:" in image


def container_image_has_newer_release(entity: dict) -> bool:
    return bool(entity.get("update_available"))


def container_image_newer_release_older_than_days(entity: dict, days: int) -> bool:
    if not entity.get("update_available"):
        return False
    age_days = entity.get("latest_release_age_days")
    if age_days is None:
        return False
    return int(age_days) > days


def container_image_release_lag_exceeds_days(entity: dict, days: int) -> bool:
    if not entity.get("update_available"):
        return False
    lag_days = entity.get("release_lag_days")
    if lag_days is None:
        return False
    return int(lag_days) > days


def container_image_within_latest_tags(entity: dict, count: int) -> bool:
    if not entity.get("release_metadata_resolved"):
        return False
    rank = entity.get("version_tag_rank")
    if rank is None:
        return False
    return int(rank) <= count


def container_image_not_within_latest_tags(entity: dict, count: int) -> bool:
    if not entity.get("release_metadata_resolved"):
        return False
    rank = entity.get("version_tag_rank")
    if rank is None:
        return True
    return int(rank) > count


def container_image_release_metadata_resolved(entity: dict) -> bool:
    return bool(entity.get("release_metadata_resolved"))


def filter_entities(
    entities: list[dict], predicate: Callable[[dict], bool]
) -> list[dict]:
    return [entity for entity in entities if predicate(entity)]


def get_inputs(entity: dict) -> dict:
    values = entity.get("values", {})
    if not isinstance(values, dict):
        return {}
    inputs = values.get("inputs")
    if inputs is None:
        inputs = values.get("variables")
    return inputs if isinstance(inputs, dict) else {}


def input_matches(entity: dict, name: str, value_spec: str) -> bool:
    inputs = get_inputs(entity)
    if name not in inputs:
        return False
    return match_value_spec(inputs.get(name), value_spec)


def get_conditional_property(entity: dict, key: str) -> Any:
    inputs = get_inputs(entity)
    if key in inputs:
        return inputs[key]
    return get_property(entity, key)


def property_matches_conditional(entity: dict, key: str, spec: str) -> bool:
    return match_value_spec(get_conditional_property(entity, key), spec)


def format_entity_ref(entity: dict) -> str:
    address = entity.get("address", entity.get("name", "unknown"))
    source_file = entity.get("source_file", "")
    line = entity.get("line", 0)
    if source_file and line:
        display_path = os.path.relpath(source_file)
        return f"{address} ({display_path}:{line})"
    return address


def assert_all(
    entities: list[dict], predicate: Callable[[dict], bool], message: str
) -> None:
    failures = [
        format_entity_ref(entity) for entity in entities if not predicate(entity)
    ]
    if failures:
        raise AssertionError(f"{message}: {', '.join(failures)}")
