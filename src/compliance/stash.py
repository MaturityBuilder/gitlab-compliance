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


def property_matches_regex(entity: dict, property_name: str, pattern: str) -> bool:
    value = normalize_value(get_property(entity, property_name))
    try:
        return re.search(pattern, value) is not None
    except re.error as exc:
        raise ValueError(f"Invalid regex pattern for property '{property_name}': {pattern}") from exc


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


def filter_entities(entities: list[dict], predicate: Callable[[dict], bool]) -> list[dict]:
    return [entity for entity in entities if predicate(entity)]


def format_entity_ref(entity: dict) -> str:
    address = entity.get("address", entity.get("name", "unknown"))
    source_file = entity.get("source_file", "")
    line = entity.get("line", 0)
    if source_file and line:
        display_path = os.path.relpath(source_file)
        return f"{address} ({display_path}:{line})"
    return address


def assert_all(entities: list[dict], predicate: Callable[[dict], bool], message: str) -> None:
    failures = [format_entity_ref(entity) for entity in entities if not predicate(entity)]
    if failures:
        raise AssertionError(f"{message}: {', '.join(failures)}")
