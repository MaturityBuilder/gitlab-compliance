"""Collect structured pipeline documentation from GitLab CI YAML."""

from __future__ import annotations

import os
from typing import Any

import semver

import src.modules.common as common

JOB_EXCLUDE_KEYWORDS = [
    "default",
    "include",
    "stages",
    "variables",
    "workflow",
    "image",
    "spec",
]

JOB_SKIP_ATTRIBUTES = {"before_script", "script", "after_script", "artifacts"}


def _normalize_include(entry: Any) -> dict:
    if isinstance(entry, str):
        return {"local": entry}
    return entry


def _include_valid_version(version: str, file: str, include: str) -> bool:
    try:
        return semver.Version.is_valid(version)
    except Exception:
        return False


def _parse_include_entry(entry: Any, source_file: str = "", line: int = 0) -> dict | None:
    include = _normalize_include(entry)
    for include_type, value in include.items():
        if include_type == "project":
            version = include.get("ref", "")
            return {
                "include_type": include_type,
                "project": value,
                "version": version,
                "valid_version": _include_valid_version(version, include.get("file", ""), value),
                "file": include.get("file", ""),
                "variables": include.get("variables", {}),
                "rules": include.get("rules", []),
                "source_file": source_file,
                "line": line,
            }
        if include_type == "component":
            try:
                project, version = value.split("@", 1)
            except ValueError:
                return None
            return {
                "include_type": include_type,
                "project": project,
                "version": version,
                "valid_version": _include_valid_version(version, "component", project),
                "file": "",
                "variables": include.get("inputs", {}),
                "rules": include.get("rules", []),
                "source_file": source_file,
                "line": line,
            }
        if include_type == "local":
            return {
                "include_type": include_type,
                "project": value,
                "version": "n/a",
                "valid_version": True,
                "file": "",
                "variables": include.get("variables", {}),
                "rules": include.get("rules", []),
                "source_file": source_file,
                "line": line,
            }
    return None


def _parse_input_entry(key: str, value: Any) -> dict:
    description = ""
    options: Any = ""
    expand = True
    if isinstance(value, dict):
        description = value.get("description", "")
        options = value.get("options", "")
        expand = value.get("expand", True)
    return {
        "key": key,
        "value": value,
        "description": description,
        "options": options,
        "expand": expand,
    }


def _parse_variable_entry(key: str, value: Any, source_file: str = "", line: int = 0) -> dict:
    description = ""
    options: Any = ""
    expand = True
    if isinstance(value, dict):
        description = value.get("description", "")
        options = value.get("options", "")
        expand = value.get("expand", True)
    return {
        "key": key,
        "value": value,
        "description": description,
        "options": options,
        "expand": expand,
        "source_file": source_file,
        "line": line,
    }


def _parse_job(name: str, config: dict, source_file: str = "", line: int = 0) -> dict:
    attributes = []
    nested = []
    rules = []

    for key in sorted(config):
        if key in JOB_SKIP_ATTRIBUTES:
            continue
        value = config[key]
        if key == "rules" and isinstance(value, list):
            rules = value
            continue
        if key == "variables" and isinstance(value, dict):
            for item_key, item_value in value.items():
                nested.append({"attribute": key, "key": item_key, "value": item_value})
            continue
        if key == "needs" and isinstance(value, list):
            for item in value:
                nested.append({"attribute": key, "key": "", "value": item})
            continue
        attributes.append({"key": key, "value": value})

    return {
        "name": name,
        "display_name": name.upper(),
        "is_template": name.startswith("."),
        "attributes": attributes,
        "rules": rules,
        "nested": nested,
        "source_file": source_file,
        "line": line,
    }


def _resolve_local_include_path(config_file: str, local_path: str) -> str | None:
    base_dir = os.path.realpath(os.path.dirname(os.path.abspath(config_file)))
    candidate = os.path.realpath(os.path.normpath(os.path.join(base_dir, local_path.lstrip("/"))))
    try:
        if os.path.commonpath([base_dir, candidate]) != base_dir:
            return None
    except ValueError:
        return None
    return candidate if os.path.exists(candidate) else None


def collect_pipeline_data(
    config_file: str,
    detailed: bool = False,
    include_nested: bool = True,
) -> dict:
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Config file not found: {config_file}")

    documents = common.read_yml(config_file)
    line_index = None
    try:
        from src.modules.yaml_lines import index_yaml_file

        line_index = index_yaml_file(config_file)
    except Exception:
        line_index = {"jobs": {}, "includes": [], "variables": {}, "workflow_rules": []}

    data: dict[str, Any] = {
        "config_file": config_file,
        "inputs": [],
        "variables": [],
        "includes": [],
        "workflow_rules": [],
        "jobs": [],
    }

    for document in documents:
        if "spec" in document and "inputs" in document["spec"]:
            for key, value in document["spec"]["inputs"].items():
                data["inputs"].append(_parse_input_entry(key, value))

        if "variables" in document:
            for key, value in document["variables"].items():
                data["variables"].append(
                    _parse_variable_entry(
                        key,
                        value,
                        source_file=config_file,
                        line=line_index["variables"].get(key, 0),
                    )
                )

        if "include" in document:
            for index, entry in enumerate(document["include"]):
                include_line = (
                    line_index["includes"][index]
                    if index < len(line_index["includes"])
                    else 0
                )
                parsed = _parse_include_entry(entry, source_file=config_file, line=include_line)
                if parsed:
                    data["includes"].append(parsed)
                    if include_nested and parsed["include_type"] == "local":
                        sub_config = _resolve_local_include_path(config_file, parsed["project"])
                        if sub_config:
                            nested = collect_pipeline_data(
                                sub_config,
                                detailed=detailed,
                                include_nested=include_nested,
                            )
                            data["includes"].extend(nested["includes"])
                            data["jobs"].extend(nested["jobs"])

        if detailed and "workflow" in document:
            workflow = document["workflow"]
            if isinstance(workflow, dict) and "rules" in workflow:
                data["workflow_rules"] = workflow["rules"]
            elif isinstance(workflow, list):
                data["workflow_rules"] = workflow

        for key, value in document.items():
            if key in JOB_EXCLUDE_KEYWORDS and not key.startswith("."):
                continue
            if not isinstance(value, dict):
                continue
            data["jobs"].append(
                _parse_job(
                    key,
                    value,
                    source_file=config_file,
                    line=line_index["jobs"].get(key, 0),
                )
            )

    return data
