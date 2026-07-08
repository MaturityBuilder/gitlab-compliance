"""Shared markdown table renderers for pipeline and gitstrings documentation."""

from __future__ import annotations

import src.modules.common as common

MISSING = "&#x274c;"


def render_inputs_table(inputs: dict) -> str:
    field_names = ["Key", "Value", "Description", "Options", "Expand"]
    table = common.table_design(headers=field_names, field_names=field_names)
    for key in inputs:
        description = MISSING
        options = MISSING
        expand = "true"
        if isinstance(inputs[key], str):
            pass
        elif isinstance(inputs[key], dict):
            entry = inputs[key]
            if "description" in entry:
                description = common.format_description_cell(entry["description"])
            if "options" in entry:
                options = entry["options"]
            if "expand" in entry:
                expand = entry["expand"]
        table.add_row([key, inputs[key], description, options, expand])
    return str(table)


def render_variables_table(variables: dict) -> str:
    field_names = ["Key", "Value", "Description", "Options", "Expand"]
    table = common.table_design(headers=field_names, field_names=field_names)
    for key in variables:
        description = MISSING
        options = MISSING
        expand = "true"
        if isinstance(variables[key], str):
            pass
        elif isinstance(variables[key], dict):
            entry = variables[key]
            if "description" in entry:
                description = common.format_description_cell(entry["description"])
            if "options" in entry:
                options = entry["options"]
            if "expand" in entry:
                expand = entry["expand"]
        table.add_row([key, variables[key], description, options, expand])
    return str(table)


def _job_like(value) -> bool:
    if not isinstance(value, dict):
        return False
    job_keys = {"stage", "script", "extends", "image", "rules", "variables"}
    return bool(job_keys & set(value.keys()))


def render_jobs_table(jobs: dict) -> str:
    parts = []
    for name, definition in jobs.items():
        if not isinstance(definition, dict):
            continue
        parts.append(f"### {name}\n")
        headers = ["Attribute", "Value"]
        table = common.table_design(headers=headers, field_names=headers)
        for attr, val in definition.items():
            if attr in ("rules", "variables") and isinstance(val, (list, dict)):
                table.add_row([attr, common.format_value(val)])
            else:
                table.add_row([attr, common.format_value(val)])
        parts.append(str(table))
        parts.append("")
    return "\n".join(parts).rstrip()


def render_generic_kv_table(data: dict) -> str:
    headers = ["Key", "Value"]
    table = common.table_design(headers=headers, field_names=headers)
    for key, value in data.items():
        table.add_row([key, common.format_value(value)])
    return str(table)
