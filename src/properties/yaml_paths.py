"""Dot-path navigation and gitstrings render/sensitive path helpers."""

from __future__ import annotations

from typing import Any

LEGACY_RENDER_MODES = frozenset(
    {"variables", "inputs", "jobs", "includes", "auto"}
)

SENSITIVE_MASK = "****"


def parse_path_list(value: str) -> list[str]:
    """Split comma-separated YAML paths (whitespace trimmed)."""
    return [part.strip() for part in value.split(",") if part.strip()]


def is_legacy_render_mode(render: str) -> bool:
    return "." not in render and render.lower() in LEGACY_RENDER_MODES


def normalize_legacy_render(render: str) -> str:
    mode = (render or "auto").lower()
    return mode if mode in LEGACY_RENDER_MODES else "auto"


def _match_dict_key(mapping: dict, key: str, *, job_names: bool) -> str | None:
    if key in mapping:
        return key
    if not job_names:
        return None
    folded = key.casefold()
    for candidate in mapping:
        if candidate.casefold() == folded:
            return candidate
    return None


def resolve_yaml_path(root: Any, path: str) -> Any | None:
    """Walk a dot-separated path; job names match case-insensitively at the pipeline root."""
    if root is None or not path or not str(path).strip():
        return None
    segments = [s for s in str(path).strip().split(".") if s]
    node: Any = root
    for index, segment in enumerate(segments):
        if not isinstance(node, dict):
            return None
        job_names = index == 0 and isinstance(root, dict)
        matched = _match_dict_key(node, segment, job_names=job_names)
        if matched is None:
            return None
        node = node[matched]
    return node


def value_path_for_variable(prefix: str, key: str, raw_value: Any) -> str:
    base = f"{prefix}.{key}" if prefix else key
    if isinstance(raw_value, dict) and "value" in raw_value:
        return f"{base}.value"
    return base


def should_mask_value(canonical_value_path: str, sensitive_paths: list[str]) -> bool:
    if not sensitive_paths:
        return False
    target = canonical_value_path.strip()
    target_variants = {target, target.removesuffix(".value"), f"{target}.value"}
    for sensitive in sensitive_paths:
        s = sensitive.strip()
        if not s:
            continue
        sensitive_variants = {s, s.removesuffix(".value"), f"{s}.value"}
        for target_variant in target_variants:
            for sensitive_variant in sensitive_variants:
                if (
                    target_variant == sensitive_variant
                    or target_variant.casefold() == sensitive_variant.casefold()
                ):
                    return True
    return False


def _mask_dict_entry_value(
    entry: dict,
    *,
    path_prefix: str,
    key: str,
    sensitive_paths: list[str],
) -> Any:
    segment = f"{path_prefix}.{key}" if path_prefix else key
    value_path = value_path_for_variable(path_prefix, key, entry)
    default_path = f"{segment}.default"
    if should_mask_value(segment, sensitive_paths) and not should_mask_value(
        value_path, sensitive_paths
    ) and not (
        "default" in entry and should_mask_value(default_path, sensitive_paths)
    ):
        return SENSITIVE_MASK
    if should_mask_value(value_path, sensitive_paths):
        masked = dict(entry)
        if "value" in masked:
            masked["value"] = SENSITIVE_MASK
        elif "default" in masked:
            masked["default"] = SENSITIVE_MASK
        else:
            return {
                sub_key: mask_sensitive_in_structure(
                    sub_value, f"{segment}.{sub_key}", sensitive_paths
                )
                for sub_key, sub_value in entry.items()
            }
        return masked
    if should_mask_value(default_path, sensitive_paths) and "default" in entry:
        masked = dict(entry)
        masked["default"] = SENSITIVE_MASK
        return masked
    return {
        sub_key: mask_sensitive_in_structure(
            sub_value, f"{segment}.{sub_key}", sensitive_paths
        )
        for sub_key, sub_value in entry.items()
    }


def mask_sensitive_in_structure(
    node: Any,
    path_prefix: str,
    sensitive_paths: list[str],
) -> Any:
    """Return a copy of YAML data with @sensitive paths replaced by SENSITIVE_MASK."""
    if not sensitive_paths:
        return node
    if isinstance(node, dict):
        masked: dict[Any, Any] = {}
        for key, value in node.items():
            segment = f"{path_prefix}.{key}" if path_prefix else key
            if isinstance(value, dict):
                masked[key] = _mask_dict_entry_value(
                    value,
                    path_prefix=path_prefix,
                    key=key,
                    sensitive_paths=sensitive_paths,
                )
            elif isinstance(value, list):
                masked[key] = [
                    mask_sensitive_in_structure(item, segment, sensitive_paths)
                    for item in value
                ]
            else:
                value_path = value_path_for_variable(path_prefix, key, value)
                if should_mask_value(value_path, sensitive_paths) or should_mask_value(
                    segment, sensitive_paths
                ):
                    masked[key] = SENSITIVE_MASK
                else:
                    masked[key] = value
        return masked
    if isinstance(node, list):
        return [
            mask_sensitive_in_structure(item, path_prefix, sensitive_paths)
            for item in node
        ]
    return node
