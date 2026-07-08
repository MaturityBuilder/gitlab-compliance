"""Shared markdown table renderers for pipeline and gitstrings documentation."""

from __future__ import annotations

import src.modules.common as common

MISSING = "&#x274c;"


def _input_row_cells(key: str, raw_value) -> list:
    description = MISSING
    options = MISSING
    expand = "true"
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
        value_cell = common.format_structured_cell(entry)
    else:
        value_cell = common.format_structured_cell(raw_value)
    return [key, value_cell, description, options, expand]


def render_inputs_table(inputs: dict) -> str:
    field_names = ["Key", "Value", "Description", "Options", "Expand"]
    table = common.table_design(headers=field_names, field_names=field_names)
    for key in inputs:
        table.add_row(_input_row_cells(key, inputs[key]))
    return str(table)


def render_variables_table(variables: dict) -> str:
    field_names = ["Key", "Value", "Description", "Options", "Expand"]
    table = common.table_design(headers=field_names, field_names=field_names)
    for key in variables:
        table.add_row(_input_row_cells(key, variables[key]))
    return str(table)


def render_jobs_table(jobs: dict) -> str:
    parts = []
    for name, definition in jobs.items():
        if not isinstance(definition, dict):
            continue
        parts.append(f"### {name}\n")
        headers = ["Attribute", "Value"]
        table = common.table_design(headers=headers, field_names=headers)
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
    table = common.table_design(headers=headers, field_names=headers)
    for key, value in data.items():
        if isinstance(value, dict):
            cell = common.format_structured_cell(value)
        else:
            cell = common.format_value(value)
        table.add_row([key, cell])
    return str(table)
