"""Shared markdown table renderers for pipeline and gitstrings documentation."""

from __future__ import annotations

import src.modules.common as common
import src.properties.yaml_paths as yaml_paths
from src.modules.logging import logger

MISSING = "&#x274c;"

_METADATA_KEYS = frozenset({"description", "options", "expand"})

_INPUTS_COLUMN_ALIGN = {
    "Key": "l",
    "Default": "l",
    "Description": "l",
    "Options": "l",
    "Expand": "c",
}

_VARIABLES_COLUMN_ALIGN = {
    "Key": "l",
    "Value": "l",
    "Description": "l",
    "Options": "l",
    "Expand": "c",
}


def _entry_field(entry: dict, field: str):
    """Read one metadata field without using ``in`` (broken mappings may override __contains__)."""
    try:
        return entry[field]
    except KeyError:
        return None
    except Exception:
        logger.error(f"Unable to read {field!r} from variable or input entry")
        return None


def _metadata_cells_from_entry(entry: dict) -> tuple[str, str, str]:
    description = MISSING
    options = MISSING
    expand = "true"
    desc_val = _entry_field(entry, "description")
    if desc_val is not None:
        description = common.format_description_cell(desc_val)
    opts_val = _entry_field(entry, "options")
    if opts_val is not None:
        options = common.format_options_cell(opts_val)
    expand_val = _entry_field(entry, "expand")
    if expand_val is not None:
        expand = expand_val
    return description, options, expand

def _inputs_row_cells(
    key: str,
    raw_value,
    *,
    path_prefix: str = "",
    sensitive_paths: list[str] | None = None,
) -> list:
    description = MISSING
    options = MISSING
    expand = "true"
    default_cell = ""

    if isinstance(raw_value, str):
        default_cell = raw_value
    elif isinstance(raw_value, dict):
        entry = raw_value
        try:
            description, options, expand = _metadata_cells_from_entry(entry)
            payload = {k: v for k, v in entry.items() if k not in _METADATA_KEYS}
            if not payload:
                default_cell = MISSING
            elif len(payload) == 1 and "default" in payload:
                default_cell = common.format_structured_cell(payload["default"])
            else:
                default_cell = common.format_structured_cell(payload)
        except Exception:
            logger.error(f"Unable to extract input information for key {key!r}")
            default_cell = common.format_structured_cell(raw_value)
    else:
        default_cell = common.format_structured_cell(raw_value)

    default_path = f"{path_prefix}.{key}" if path_prefix else key
    if isinstance(raw_value, dict) and _entry_field(raw_value, "default") is not None:
        default_path = f"{default_path}.default"
    if yaml_paths.should_mask_value(default_path, sensitive_paths or []):
        default_cell = yaml_paths.SENSITIVE_MASK

    return [key, default_cell, description, options, expand]


def _variables_row_cells(
    key: str,
    raw_value,
    *,
    path_prefix: str = "",
    sensitive_paths: list[str] | None = None,
) -> list:
    description = MISSING
    options = MISSING
    expand = "true"
    value_cell = ""

    if isinstance(raw_value, str):
        value_cell = raw_value
    elif isinstance(raw_value, dict):
        entry = raw_value
        try:
            description, options, expand = _metadata_cells_from_entry(entry)
            payload = {k: v for k, v in entry.items() if k not in _METADATA_KEYS}
            if not payload:
                value_cell = MISSING
            elif len(payload) == 1 and "value" in payload:
                value_cell = common.format_structured_cell(payload["value"])
            else:
                value_cell = common.format_structured_cell(payload)
        except Exception:
            logger.error(f"Unable to extract variable information for key {key!r}")
            val = _entry_field(entry, "value")
            if val is not None:
                value_cell = common.format_structured_cell(val)
            else:
                value_cell = common.format_structured_cell(raw_value)
    else:
        value_cell = common.format_structured_cell(raw_value)

    value_path = yaml_paths.value_path_for_variable(path_prefix, key, raw_value)
    if yaml_paths.should_mask_value(value_path, sensitive_paths or []):
        value_cell = yaml_paths.SENSITIVE_MASK

    return [key, value_cell, description, options, expand]


def render_inputs_table(
    inputs: dict,
    *,
    path_prefix: str = "",
    sensitive_paths: list[str] | None = None,
) -> str:
    field_names = ["Key", "Default", "Description", "Options", "Expand"]
    table = common.table_design(
        headers=field_names,
        field_names=field_names,
        column_align=_INPUTS_COLUMN_ALIGN,
    )
    for key in inputs:
        table.add_row(
            _inputs_row_cells(
                key,
                inputs[key],
                path_prefix=path_prefix,
                sensitive_paths=sensitive_paths,
            )
        )
    return common.markdown_table_from_prettytable(table)


def render_variables_table(
    variables: dict,
    *,
    path_prefix: str = "",
    sensitive_paths: list[str] | None = None,
) -> str:
    field_names = ["Key", "Value", "Description", "Options", "Expand"]
    table = common.table_design(
        headers=field_names,
        field_names=field_names,
        column_align=_VARIABLES_COLUMN_ALIGN,
    )
    for key in variables:
        table.add_row(
            _variables_row_cells(
                key,
                variables[key],
                path_prefix=path_prefix,
                sensitive_paths=sensitive_paths,
            )
        )
    return common.markdown_table_from_prettytable(table)


def render_jobs_table(jobs: dict) -> str:
    parts = []
    for name, definition in jobs.items():
        if not isinstance(definition, dict):
            continue
        parts.append(f"### {name}\n")
        headers = ["Attribute", "Value"]
        table = common.table_design(
            headers=headers,
            field_names=headers,
            column_align={"Attribute": "l", "Value": "l"},
        )
        for attr, val in definition.items():
            if isinstance(val, dict):
                cell = common.format_structured_cell(val)
            else:
                cell = common.format_value(val)
            table.add_row([attr, cell])
        parts.append(common.markdown_table_from_prettytable(table))
        parts.append("")
    return "\n".join(parts).rstrip()


def render_generic_kv_table(
    data: dict,
    *,
    path_prefix: str = "",
    sensitive_paths: list[str] | None = None,
) -> str:
    headers = ["Key", "Value"]
    table = common.table_design(
        headers=headers,
        field_names=headers,
        column_align={"Key": "l", "Value": "l"},
    )
    for key, value in data.items():
        if isinstance(value, dict):
            cell = common.format_structured_cell(value)
        else:
            cell = common.format_value(value)
        value_path = f"{path_prefix}.{key}" if path_prefix else key
        if yaml_paths.should_mask_value(value_path, sensitive_paths or []):
            cell = yaml_paths.SENSITIVE_MASK
        table.add_row([key, cell])
    return common.markdown_table_from_prettytable(table)


def render_path_markdown(
    root: dict,
    path: str,
    *,
    sensitive_paths: list[str] | None = None,
) -> str:
    """Render markdown tables for a dot-path into pipeline YAML."""
    sensitive_paths = sensitive_paths or []
    node = yaml_paths.resolve_yaml_path(root, path)
    if node is None:
        return ""

    segments = [s for s in path.split(".") if s]
    last = segments[-1] if segments else ""

    if path == "inputs" or path.endswith(".inputs"):
        inputs = node if isinstance(node, dict) else {}
        return render_inputs_table(
            inputs, path_prefix=path, sensitive_paths=sensitive_paths
        )

    if ".inputs." in path:
        parent = ".".join(segments[:-1])
        return render_inputs_table(
            {last: node},
            path_prefix=parent,
            sensitive_paths=sensitive_paths,
        )

    if path == "variables" or path.endswith(".variables"):
        variables = node if isinstance(node, dict) else {}
        return render_variables_table(
            variables, path_prefix=path, sensitive_paths=sensitive_paths
        )

    if ".variables." in path:
        parent = ".".join(segments[:-1])
        return render_variables_table(
            {last: node},
            path_prefix=parent,
            sensitive_paths=sensitive_paths,
        )

    if last == "variables" and isinstance(node, dict):
        return render_variables_table(
            node, path_prefix=path, sensitive_paths=sensitive_paths
        )

    if len(segments) == 1 and isinstance(node, dict):
        return render_jobs_table({segments[0]: node})

    return render_generic_kv_table(
        {last or path: node},
        path_prefix=".".join(segments[:-1]) if len(segments) > 1 else "",
        sensitive_paths=sensitive_paths,
    )
