import logging
from pathlib import Path
from typing import Any

import semver

from gitlab_docs import jobs as jobs_module
from gitlab_docs.constants import NON_SEMVER_REFS
from gitlab_docs.render import DocTable, render_table
from gitlab_docs.yaml_load import load_ci_config

logger = logging.getLogger("gitlab_docs.includes")

INCLUDE_TYPES = ("local", "project", "remote", "component", "template")


def _ref_validity_label(version: str) -> str:
    if version in NON_SEMVER_REFS:
        return "branch/tag"
    if semver.Version.is_valid(version):
        return "&#9989;"
    return "&#x274c;"


def check_include_version_is_sema_version(version: str, file: str, include: str) -> bool:
    if version in NON_SEMVER_REFS:
        return True
    valid = semver.Version.is_valid(version)
    if not valid:
        logger.warning(
            "Ref is not semver %s | file=%s | include=%s",
            version,
            file,
            include,
        )
    return valid


def _normalize_include_item(item: Any) -> dict:
    if isinstance(item, str):
        return {"local": item}
    if isinstance(item, dict):
        return item
    return {"local": str(item)}


def _include_kind(item: dict) -> str | None:
    for kind in INCLUDE_TYPES:
        if kind in item:
            return kind
    return None


def _component_parts(component_url: str) -> tuple[str, str]:
    if "@" not in component_url:
        logger.warning("Component URL has no @ref: %s", component_url)
        return component_url, "n/a"
    project, ref = component_url.rsplit("@", 1)
    return project, ref


def _row_for_include(item: dict) -> list[str] | None:
    kind = _include_kind(item)
    if kind is None:
        logger.warning("Unknown include entry: %s", item)
        return None

    inc_vars = item.get("variables") or item.get("inputs") or ""
    inc_rules = item.get("rules") or ""

    if kind == "local":
        path = item["local"]
        return [kind, path, "n/a", "&#9989;", "", str(inc_vars), str(inc_rules)]

    if kind == "project":
        version = item.get("ref", "n/a")
        project = item["project"]
        file_name = item.get("file", "")
        valid = _ref_validity_label(str(version))
        return [kind, project, str(version), valid, str(file_name), str(inc_vars), str(inc_rules)]

    if kind == "component":
        project, version = _component_parts(item["component"])
        valid = _ref_validity_label(version)
        return [kind, project, version, valid, "", str(inc_vars), str(inc_rules)]

    if kind == "remote":
        return [
            kind,
            item.get("remote", ""),
            "n/a",
            "&#9989;",
            "",
            str(inc_vars),
            str(inc_rules),
        ]

    if kind == "template":
        return [
            kind,
            item.get("template", ""),
            "n/a",
            "&#9989;",
            "",
            str(inc_vars),
            str(inc_rules),
        ]

    return None


def _local_include_path(base_config: Path, local_path: str) -> Path:
    resolved = Path(local_path)
    if not resolved.is_absolute():
        resolved = (base_config.parent / resolved).resolve()
    if str(local_path).startswith("/"):
        return Path(str(local_path).lstrip("/"))
    return resolved


def build_includes_section(
    config_file: Path,
    data: dict | None = None,
    *,
    output_format: str = "markdown",
    disable_type_heading: bool = False,
    _visited: set[Path] | None = None,
) -> str:
    if data is None:
        data = load_ci_config(config_file)

    if _visited is None:
        _visited = set()

    config_file = config_file.resolve()
    if config_file in _visited:
        logger.warning("Skipping circular include: %s", config_file)
        return ""
    _visited.add(config_file)

    includes_list = data.get("include")
    if includes_list is None:
        includes_list = []
    if not isinstance(includes_list, list):
        includes_list = [includes_list]

    table = DocTable(
        headers=[
            "Include Type",
            "Project",
            "Version",
            "Valid Version",
            "File",
            "Variables",
            "Rules",
        ],
    )

    nested_parts: list[str] = []
    for raw in includes_list:
        item = _normalize_include_item(raw)
        row = _row_for_include(item)
        if row:
            table.add_row(row)

        kind = _include_kind(item)
        if kind != "local":
            continue

        sub_path = _local_include_path(config_file, item["local"])
        if not sub_path.is_file():
            logger.warning("Local include not found: %s", sub_path)
            continue

        nested = build_includes_section(
            sub_path,
            output_format=output_format,
            disable_type_heading=disable_type_heading,
            _visited=_visited,
        )
        if nested:
            nested_parts.append(nested)

        jobs_part = jobs_module.build_jobs_section(
            sub_path,
            output_format=output_format,
            disable_title=True,
            disable_type_heading=disable_type_heading,
        )
        if jobs_part:
            nested_parts.append(jobs_part)

    parts: list[str] = list(nested_parts)
    if table.rows:
        heading = "" if disable_type_heading else "## Includes\n\n"
        parts.append(heading + render_table(table, output_format))

    return "\n\n".join(part for part in parts if part).strip()


def document_includes(
    OUTPUT_FILE,
    GLDOCS_CONFIG_FILE,
    WRITE_MODE="a",
    DISABLE_TITLE=False,
    DISABLE_TYPE_HEADING=True,
):
    from gitlab_docs.reset_docs import write_documentation

    body = build_includes_section(
        Path(GLDOCS_CONFIG_FILE),
        output_format="markdown",
        disable_type_heading=DISABLE_TYPE_HEADING,
    )
    if body:
        write_documentation(OUTPUT_FILE, body, "markdown")
