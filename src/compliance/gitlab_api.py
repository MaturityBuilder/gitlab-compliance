"""Load GitLab project/group settings via API for compliance checks."""

from __future__ import annotations

import os
from typing import Any


PROJECT_SETTING_KEYS = [
    "public_jobs",
    "auto_devops_enabled",
    "builds_access_level",
    "forking_access_level",
    "merge_requests_enabled",
    "jobs_enabled",
]


def _setting_entity(setting_type: str, name: str, value: Any) -> dict:
    return {
        "address": f"{setting_type}.{name}",
        "type": setting_type,
        "name": name,
        "value": value,
        "values": {"value": value},
    }


def _ci_variable_entity(variable: Any) -> dict:
    return {
        "address": f"project_ci_variable.{variable.key}",
        "type": "project_ci_variable",
        "name": variable.key,
        "key": variable.key,
        "value": "***",
        "protected": getattr(variable, "protected", False),
        "masked": getattr(variable, "masked", False),
        "values": {
            "key": variable.key,
            "protected": getattr(variable, "protected", False),
            "masked": getattr(variable, "masked", False),
        },
    }


def load_api_entities(
    gitlab_url: str | None = None,
    token: str | None = None,
    project: str | None = None,
    group: str | None = None,
    gl: Any | None = None,
) -> dict[str, list[dict]]:
    gitlab_url = gitlab_url or os.getenv("CI_SERVER_URL") or os.getenv("GITLAB_URL") or "https://gitlab.com"
    token = token or os.getenv("GITLAB_TOKEN") or os.getenv("CI_JOB_TOKEN")

    if not token:
        raise ValueError("GitLab API token required. Set --token or GITLAB_TOKEN.")

    if gl is None:
        import gitlab

        gl = gitlab.Gitlab(gitlab_url, private_token=token)
        gl.auth()

    entities: dict[str, list[dict]] = {
        "project_settings": [],
        "project_ci_variables": [],
        "group_settings": [],
    }

    if project:
        project_obj = gl.projects.get(project)
        for key in PROJECT_SETTING_KEYS:
            if hasattr(project_obj, key):
                entities["project_settings"].append(
                    _setting_entity("project_setting", key, getattr(project_obj, key))
                )

        for variable in project_obj.variables.list(all=True):
            entities["project_ci_variables"].append(_ci_variable_entity(variable))

    if group:
        group_obj = gl.groups.get(group)
        for attr in ("shared_runners_enabled", "request_access_enabled"):
            if hasattr(group_obj, attr):
                entities["group_settings"].append(
                    _setting_entity("group_setting", attr, getattr(group_obj, attr))
                )

    return entities
