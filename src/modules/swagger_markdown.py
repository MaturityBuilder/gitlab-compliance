"""Render pipeline documentation as Swagger-structured Markdown."""

from __future__ import annotations

import re

import src.modules.common as common


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _is_section_excluded(data: dict, section: str) -> bool:
    return section in data.get("exclude_sections", set())


def _render_rules_section(
    rules: list[dict], title: str, heading: str = "###"
) -> list[str]:
    if not rules:
        return []
    body = common.render_rules_markdown(rules)
    if not body:
        return []
    return [f"{heading} {title}", "", body, ""]


def _job_summary(job: dict) -> str:
    bits = []
    for item in job["attributes"][:3]:
        bits.append(f"{item['key']}: {common.format_value(item['value'])}")
    summary = " · ".join(bits) if bits else "No attributes documented."
    if len(summary) > 76:
        return summary[:73] + "..."
    return summary


def _render_job_block(job: dict) -> list[str]:
    kind = "TEMPLATE" if job["is_template"] else "JOB"
    name = job["display_name"]
    lines = [
        f"### {kind} · {name}",
        "",
        f"> {_job_summary(job)}",
        "",
    ]

    attribute_rows = [
        [item["key"], common.format_value(item["value"])] for item in job["attributes"]
    ]
    if attribute_rows:
        lines.extend(
            [
                f"#### {name} · attributes",
                "",
                common.render_table_or_list(["Attribute", "Value"], attribute_rows),
                "",
            ]
        )

    lines.extend(_render_rules_section(job["rules"], f"{name} · rules", "####"))

    nested_rows = [
        [item["attribute"], item["key"], common.format_value(item["value"])]
        for item in job["nested"]
    ]
    if nested_rows:
        lines.extend(
            [
                f"#### {name} · nested attributes",
                "",
                common.render_table_or_list(["Attribute", "Key", "Value"], nested_rows),
                "",
            ]
        )

    lines.extend(["---", ""])
    return lines


def _jobs_grouped(data: dict) -> list[dict]:
    """Return grouped jobs, falling back to a flat list when unfiltered."""
    grouped = data.get("jobs_grouped")
    if grouped is not None:
        return grouped
    jobs = data.get("jobs", [])
    return [{"group_key": "", "jobs": jobs}]


def _render_jobs_section(data: dict) -> list[str]:
    lines: list[str] = []
    group_by = data.get("group_by")

    for block in _jobs_grouped(data):
        group_key = block.get("group_key", "")
        if group_by and group_key:
            lines.extend(
                [
                    f"### {group_by.title()} · {group_key}",
                    "",
                ]
            )
        for job in block.get("jobs", []):
            lines.extend(_render_job_block(job))

    return lines


def render_swagger_markdown(data: dict) -> str:
    config_file = data["config_file"]
    lines = [
        f"# GitLab pipeline reference — `{config_file}`",
        "",
        f"- **Config file:** `{config_file}`",
        f"- **Jobs:** {len(data['jobs'])}",
        "",
        "## Contents",
        "",
    ]

    if not _is_section_excluded(data, "inputs"):
        lines.append("- [Inputs](#inputs)")
    if not _is_section_excluded(data, "variables"):
        lines.append("- [Variables](#variables)")
    if not _is_section_excluded(data, "includes"):
        lines.append("- [Includes](#includes)")
    if data["workflow_rules"] and not _is_section_excluded(data, "workflow"):
        lines.append("- [Workflow](#workflow)")
    if not _is_section_excluded(data, "jobs"):
        lines.append(f"- [Jobs](#jobs) ({len(data['jobs'])})")
        group_by = data.get("group_by")
        if group_by:
            for block in _jobs_grouped(data):
                group_key = block.get("group_key", "")
                if group_key:
                    lines.append(f"  - {group_by.title()} · {group_key}")
        else:
            for job in data["jobs"]:
                lines.append(f"  - {job['display_name']}")

    if not _is_section_excluded(data, "inputs"):
        lines.extend(["", "## Inputs", ""])
        if data["inputs"]:
            input_rows = [
                [
                    item["key"],
                    item["value"],
                    item["description"],
                    item["options"],
                    item["expand"],
                ]
                for item in data["inputs"]
            ]
            lines.append(
                common.render_table_or_list(
                    ["Key", "Value", "Description", "Options", "Expand"], input_rows
                )
            )
        else:
            lines.append("_No inputs defined._")
        lines.append("")

    if not _is_section_excluded(data, "variables"):
        lines.extend(["## Variables", ""])
        if data["variables"]:
            variable_rows = [
                [
                    item["key"],
                    item["value"],
                    item["description"],
                    item["options"],
                    item["expand"],
                ]
                for item in data["variables"]
            ]
            lines.append(
                common.render_table_or_list(
                    ["Key", "Value", "Description", "Options", "Expand"], variable_rows
                )
            )
        else:
            lines.append("_No variables defined._")
        lines.append("")

    if not _is_section_excluded(data, "includes"):
        lines.extend(["## Includes", ""])
        if data["includes"]:
            for item in data["includes"]:
                lines.extend(
                    [
                        f"- **{item['include_type']}:** `{item['project']}`",
                        f"  - **version:** `{item['version']}`",
                        f"  - **valid:** {'yes' if item['valid_version'] else 'no'}",
                    ]
                )
                if item["file"]:
                    lines.append(f"  - **file:** `{item['file']}`")
                variables = common.format_dict_summary(item["variables"])
                if variables:
                    lines.append(f"  - **variables:** `{variables}`")
                rules = common.format_rules_summary(item["rules"])
                if rules:
                    lines.append(f"  - **rules:** `{rules}`")
                lines.append("")
        else:
            lines.append("_No includes defined._")
            lines.append("")

    if data["workflow_rules"] and not _is_section_excluded(data, "workflow"):
        lines.extend(["## Workflow", ""])
        lines.extend(_render_rules_section(data["workflow_rules"], "workflow rules"))

    if not _is_section_excluded(data, "jobs"):
        lines.extend(["## Jobs", ""])
        job_lines = _render_jobs_section(data)
        if job_lines:
            lines.extend(job_lines)
        else:
            lines.append("_No jobs found._")
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"
