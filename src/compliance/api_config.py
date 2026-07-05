"""Resolve GitLab API connection settings for compliance checks."""

from __future__ import annotations

import os
from typing import Any, Literal

ApiScope = Literal["project", "group"]


def _userdata_value(userdata: dict[str, Any], key: str) -> str | None:
    value = userdata.get(key)
    if value:
        return str(value)
    return None


def resolve_token(userdata: dict[str, Any] | None = None) -> str | None:
    # Tokens must not be passed through Behave userdata (may appear in logs/reports).
    return os.getenv("GITLAB_TOKEN") or os.getenv("CI_JOB_TOKEN")


def resolve_project(userdata: dict[str, Any] | None = None) -> str | None:
    userdata = userdata or {}
    return _userdata_value(userdata, "project") or os.getenv("CI_PROJECT_PATH")


def resolve_group(userdata: dict[str, Any] | None = None) -> str | None:
    userdata = userdata or {}
    return _userdata_value(userdata, "group") or os.getenv("GITLAB_GROUP_PATH")


def project_api_ready(userdata: dict[str, Any] | None = None) -> bool:
    return bool(resolve_token(userdata) and resolve_project(userdata))


def group_api_ready(userdata: dict[str, Any] | None = None) -> bool:
    return bool(resolve_token(userdata) and resolve_group(userdata))


def _missing_connection_message(scope: ApiScope, label: str) -> str:
    if scope == "project":
        return (
            f"GitLab API connection info not provided for {label}. "
            "Set --token and --project (or GITLAB_TOKEN/CI_JOB_TOKEN and CI_PROJECT_PATH)."
        )
    return (
        f"GitLab API connection info not provided for {label}. "
        "Set --token and --group (or GITLAB_TOKEN/CI_JOB_TOKEN)."
    )


def require_api_connection(context, scope: ApiScope, label: str) -> bool:
    userdata = context.config.userdata
    ready = project_api_ready(userdata) if scope == "project" else group_api_ready(userdata)
    if ready:
        return True

    message = _missing_connection_message(scope, label)
    if userdata.get("strict") == "true":
        raise AssertionError(message)

    from src.compliance.behave_support.environment import _skip_remaining_steps

    _skip_remaining_steps(context, message)
    return False
