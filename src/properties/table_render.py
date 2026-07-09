"""Shared markdown table renderers for pipeline and gitstrings documentation."""

from __future__ import annotations

import src.modules.common as common
import src.properties.yaml_paths as yaml_paths
from src.modules.logging import logger

MISSING = "&#x274c;"

_METADATA_KEYS = frozenset({"description", "options", "expand"})


def _gitstrings_table_cell(value) -> str:
    """Format YAML values for gitstrings pipe tables (no bullet/numbered lists)."""
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return common.format_structured_cell(value)
    return common.format_scalar(value)


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


def _rule_value(rule: dict, key: str) -> str:
    value = rule.get(key)
    if value is None:
        return ""
    return _gitstrings_table_cell(value)


def render_rules_table(rules: list, *, context: str = "job") -> str:
    """Render GitLab job or workflow rules with a short behavior note."""
    if context == "workflow":
        note = (
            "> Workflow rules are evaluated in order before jobs are created; "
            "the first matching rule decides whether the pipeline runs.\n"
        )
    else:
        note = (
            "> Job rules are evaluated in order; the first matching rule decides "
            "whether the job is added to the pipeline and which `when` behavior applies.\n"
        )

    headers = ["Rule", "If", "When", "Changes", "Exists", "Allow failure"]
    table = common.table_design(
        headers=headers,
        field_names=headers,
        column_align={header: "l" for header in headers},
    )
    for index, rule in enumerate(rules, start=1):
        if not isinstance(rule, dict):
            table.add_row([index, _gitstrings_table_cell(rule), "", "", "", ""])
            continue
        table.add_row(
            [
                index,
                _rule_value(rule, "if"),
                _rule_value(rule, "when"),
                _rule_value(rule, "changes"),
                _rule_value(rule, "exists"),
                _rule_value(rule, "allow_failure"),
            ]
        )
    return note + "\n" + common.markdown_table_from_prettytable(table)


def render_jobs_table(jobs: dict) -> str:
    parts = []
    for name, definition in jobs.items():
        if not isinstance(definition, dict):
            continue
        parts.append(f"### {name}\n")
        if isinstance(definition.get("rules"), list):
            parts.append(
                "> This job defines `rules`; see the `rules` attribute for the "
                "ordered conditions that control when it is added to a pipeline.\n"
            )
        headers = ["Attribute", "Value"]
        table = common.table_design(
            headers=headers,
            field_names=headers,
            column_align={"Attribute": "l", "Value": "l"},
        )
        for attr, val in definition.items():
            table.add_row([attr, _gitstrings_table_cell(val)])
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
        cell = _gitstrings_table_cell(value)
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

    if last == "rules" and isinstance(node, list):
        context = "workflow" if segments[:2] == ["workflow", "rules"] else "job"
        return render_rules_table(node, context=context)

    if (
        path == "workflow"
        and isinstance(node, dict)
        and isinstance(node.get("rules"), list)
    ):
        parts = [render_rules_table(node["rules"], context="workflow")]
        remaining = {key: value for key, value in node.items() if key != "rules"}
        if remaining:
            parts.append(
                render_generic_kv_table(
                    remaining,
                    path_prefix=path,
                    sensitive_paths=sensitive_paths,
                )
            )
        return "\n\n".join(parts)

    if len(segments) == 1 and isinstance(node, dict):
        return render_jobs_table({segments[0]: node})

    return render_generic_kv_table(
        {last or path: node},
        path_prefix=".".join(segments[:-1]) if len(segments) > 1 else "",
        sensitive_paths=sensitive_paths,
    )
