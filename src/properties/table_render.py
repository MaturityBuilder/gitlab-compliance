"""Shared markdown table renderers for pipeline and gitstrings documentation."""

from __future__ import annotations

import src.modules.common as common

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


def _inputs_row_cells(key: str, raw_value) -> list:
    description = MISSING
    options = MISSING
    expand = "true"
    default_cell = ""

    if isinstance(raw_value, str):
        default_cell = raw_value
    elif isinstance(raw_value, dict):
        entry = raw_value
        if "description" in entry:
            description = common.format_description_cell(entry["description"])
        if "options" in entry:
            options = common.format_options_cell(entry["options"])
        if "expand" in entry:
            expand = entry["expand"]
        payload = {k: v for k, v in entry.items() if k not in _METADATA_KEYS}
        if not payload:
            default_cell = MISSING
        elif len(payload) == 1 and "default" in payload:
            default_cell = common.format_structured_cell(payload["default"])
        else:
            default_cell = common.format_structured_cell(payload)
    else:
        default_cell = common.format_structured_cell(raw_value)

    return [key, default_cell, description, options, expand]


def _variables_row_cells(key: str, raw_value) -> list:
    description = MISSING
    options = MISSING
    expand = "true"
    value_cell = ""

    if isinstance(raw_value, str):
        value_cell = raw_value
    elif isinstance(raw_value, dict):
        entry = raw_value
        if "description" in entry:
            description = common.format_description_cell(entry["description"])
        if "options" in entry:
            options = common.format_options_cell(entry["options"])
        if "expand" in entry:
            expand = entry["expand"]
        payload = {k: v for k, v in entry.items() if k not in _METADATA_KEYS}
        if not payload:
            value_cell = MISSING
        elif len(payload) == 1 and "value" in payload:
            value_cell = common.format_structured_cell(payload["value"])
        else:
            value_cell = common.format_structured_cell(payload)
    else:
        value_cell = common.format_structured_cell(raw_value)

    return [key, value_cell, description, options, expand]


def render_inputs_table(inputs: dict) -> str:
    field_names = ["Key", "Default", "Description", "Options", "Expand"]
    table = common.table_design(
        headers=field_names,
        field_names=field_names,
        column_align=_INPUTS_COLUMN_ALIGN,
    )
    for key in inputs:
        table.add_row(_inputs_row_cells(key, inputs[key]))
    return common.markdown_table_from_prettytable(table)


def render_variables_table(variables: dict) -> str:
    field_names = ["Key", "Value", "Description", "Options", "Expand"]
    table = common.table_design(
        headers=field_names,
        field_names=field_names,
        column_align=_VARIABLES_COLUMN_ALIGN,
    )
    for key in variables:
        table.add_row(_variables_row_cells(key, variables[key]))
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
        parts.append(str(table))
        parts.append("")
    return "\n".join(parts).rstrip()


def render_generic_kv_table(data: dict) -> str:
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
        table.add_row([key, cell])
    return str(table)
