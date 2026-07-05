"""Load GitLab CI YAML into compliance entity stash."""

from __future__ import annotations

import os
from typing import Any

from src.modules.pipeline_data import collect_pipeline_data


def _job_entity(name: str, config: dict, source_file: str = "", line: int = 0) -> dict:
    return {
        "address": f"job.{name}",
        "type": "job",
        "name": name,
        "values": dict(config),
        "source_file": source_file,
        "line": line,
    }


def _include_entity(index: int, include: dict) -> dict:
    return {
        "address": f"include.{index}",
        "type": "include",
        "include_type": include["include_type"],
        "name": include.get("project", ""),
        "project": include.get("project", ""),
        "version": include.get("version", ""),
        "file": include.get("file", ""),
        "values": include,
        "source_file": include.get("source_file", ""),
        "line": include.get("line", 0),
    }


def _variable_entity(key: str, value: Any, source_file: str = "", line: int = 0) -> dict:
    return {
        "address": f"variable.{key}",
        "type": "variable",
        "name": key,
        "key": key,
        "value": value,
        "values": {"value": value},
        "source_file": source_file,
        "line": line,
    }


def _workflow_rule_entity(index: int, rule: Any, source_file: str = "", line: int = 0) -> dict:
    return {
        "address": f"workflow.rule.{index}",
        "type": "workflow_rule",
        "name": f"rule-{index}",
        "values": rule if isinstance(rule, dict) else {"rule": rule},
        "source_file": source_file,
        "line": line,
    }


def load_yaml_entities(
    pipeline_file: str,
    include_nested: bool = True,
) -> dict[str, list[dict]]:
    if not os.path.exists(pipeline_file):
        raise FileNotFoundError(f"Pipeline file not found: {pipeline_file}")

    pipeline_data = collect_pipeline_data(
        config_file=pipeline_file,
        detailed=True,
        include_nested=include_nested,
    )

    from src.modules.yaml_lines import index_yaml_file

    line_index = index_yaml_file(pipeline_file)
    workflow_rule_lines = line_index.get("workflow_rules", [])

    entities: dict[str, list[dict]] = {
        "jobs": [
            _job_entity(job["name"], _job_values(job), job.get("source_file", pipeline_file), job.get("line", 0))
            for job in pipeline_data["jobs"]
        ],
        "includes": [
            _include_entity(index, include)
            for index, include in enumerate(pipeline_data["includes"])
        ],
        "variables": [
            _variable_entity(
                item["key"],
                item["value"],
                item.get("source_file", pipeline_file),
                item.get("line", 0),
            )
            for item in pipeline_data["variables"]
        ],
        "workflow_rules": [
            _workflow_rule_entity(
                index,
                rule,
                pipeline_file,
                workflow_rule_lines[index - 1] if index - 1 < len(workflow_rule_lines) else 0,
            )
            for index, rule in enumerate(pipeline_data["workflow_rules"], 1)
        ],
        "project_settings": [],
        "project_ci_variables": [],
        "group_settings": [],
    }
    return entities


def _job_values(job: dict) -> dict:
    values = {}
    for attribute in job.get("attributes", []):
        values[attribute["key"]] = attribute["value"]
    if job.get("rules"):
        values["rules"] = job["rules"]
    for nested in job.get("nested", []):
        if nested["attribute"] == "variables":
            values.setdefault("variables", {})
            values["variables"][nested["key"]] = nested["value"]
        elif nested["attribute"] == "needs":
            values.setdefault("needs", [])
            values["needs"].append(nested["value"])
    return values


def load_pipeline_entities(
    pipeline_file: str,
    include_nested: bool = True,
    gitlab_url: str | None = None,
    token: str | None = None,
    project: str | None = None,
    group: str | None = None,
) -> dict[str, list[dict]]:
    from src.compliance.api_config import resolve_group, resolve_project, resolve_token

    entities = load_yaml_entities(pipeline_file, include_nested=include_nested)

    userdata = {
        "project": project or "",
        "group": group or "",
    }
    api_token = token or resolve_token(userdata)
    resolved_project = resolve_project(userdata)
    resolved_group = resolve_group(userdata)

    if api_token and (resolved_project or resolved_group):
        from src.compliance.gitlab_api import load_api_entities

        api_entities = load_api_entities(
            gitlab_url=gitlab_url,
            token=api_token,
            project=resolved_project,
            group=resolved_group,
        )
        entities["project_settings"].extend(api_entities.get("project_settings", []))
        entities["project_ci_variables"].extend(api_entities.get("project_ci_variables", []))
        entities["group_settings"].extend(api_entities.get("group_settings", []))

    return entities
