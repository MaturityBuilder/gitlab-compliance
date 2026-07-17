"""GitLab merge request helpers for compliance check."""

from __future__ import annotations

import os
import re
from datetime import datetime, timezone

import gitlab

from src.compliance.api_config import resolve_project
from src.modules.logging import logger

_FIX_PATH_RE = re.compile(r"\((?:[^()]*?,\s*)?(?P<path>[^(),]+):(?P<line>\d+)\)\s*$")


def _resolve_gitlab_url(gitlab_url: str | None) -> str:
    return (
        gitlab_url
        or os.getenv("CI_SERVER_URL")
        or os.getenv("GITLAB_URL")
        or "https://gitlab.com"
    )


def _resolve_project_path(project: str | None) -> str:
    resolved = project or resolve_project(None)
    if not resolved:
        raise ValueError(
            "GitLab project is required. Set --project or CI_PROJECT_PATH."
        )
    return resolved


def _changed_files_from_fix_messages(fix_messages: list[str]) -> list[str]:
    paths: list[str] = []
    seen: set[str] = set()
    for message in fix_messages:
        match = _FIX_PATH_RE.search(message)
        if not match:
            continue
        path = match.group("path").strip()
        if path and path not in seen:
            seen.add(path)
            paths.append(path)
    return paths


def _repo_relative_path(path: str, pipeline_file: str) -> str:
    abs_path = os.path.realpath(os.path.abspath(path))
    roots: list[str] = []
    project_dir = os.getenv("CI_PROJECT_DIR")
    if project_dir:
        roots.append(os.path.realpath(project_dir))
    roots.append(os.path.realpath(os.getcwd()))
    roots.append(os.path.dirname(os.path.realpath(os.path.abspath(pipeline_file))))
    for root in roots:
        try:
            if os.path.commonpath([root, abs_path]) == root:
                return os.path.relpath(abs_path, root).replace(os.sep, "/")
        except ValueError:
            continue
    return path.replace(os.sep, "/")


def _default_branch_name() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"gitlab-compliance/supply-chain-fix-{stamp}"


def create_supply_chain_merge_request(
    *,
    pipeline_file: str,
    fix_messages: list[str],
    gitlab_url: str | None,
    token: str,
    project: str | None,
    branch_name: str | None = None,
    target_branch: str | None = None,
) -> str | None:
    """Commit fixed files and open an MR. Returns the MR web URL or None."""
    if not token:
        raise ValueError(
            "--create-mr requires a GitLab token (--token, GITLAB_TOKEN, or CI_JOB_TOKEN)"
        )
    changed = _changed_files_from_fix_messages(fix_messages)
    if not changed:
        logger.info("No supply-chain file changes to commit; skipping --create-mr.")
        return None

    project_path = _resolve_project_path(project)
    url = _resolve_gitlab_url(gitlab_url)
    gl = gitlab.Gitlab(url, private_token=token)
    project_obj = gl.projects.get(project_path)
    target = target_branch or project_obj.default_branch
    branch = branch_name or _default_branch_name()

    try:
        project_obj.branches.get(branch)
    except gitlab.exceptions.GitlabGetError:
        project_obj.branches.create({"branch": branch, "ref": target})

    actions = []
    for path in changed:
        if not os.path.exists(path):
            logger.warning(f"Skipping missing fixed file for MR: {path}")
            continue
        with open(path, encoding="utf-8") as handle:
            content = handle.read()
        actions.append(
            {
                "action": "update",
                "file_path": _repo_relative_path(path, pipeline_file),
                "content": content,
            }
        )
    if not actions:
        logger.info("No readable fixed files for MR commit; skipping --create-mr.")
        return None

    commit_message = "fix: apply gitlab-compliance supply-chain updates"
    project_obj.commits.create(
        {
            "branch": branch,
            "commit_message": commit_message,
            "actions": actions,
        }
    )

    description_lines = [
        "Automated supply-chain updates from `gitlab-compliance check --fix`.",
        "",
        "### Changes",
        "",
    ]
    description_lines.extend(f"- {message}" for message in fix_messages)
    merge_request = project_obj.mergerequests.create(
        {
            "source_branch": branch,
            "target_branch": target,
            "title": "fix: gitlab-compliance supply-chain updates",
            "description": "\n".join(description_lines),
            "remove_source_branch": True,
        }
    )
    web_url = getattr(merge_request, "web_url", None) or ""
    logger.info(f"Created merge request: {web_url or merge_request.iid}")
    return web_url or str(merge_request.iid)


def post_compliance_mr_comment(
    *,
    body: str,
    gitlab_url: str | None,
    token: str,
    project: str | None,
    mr_iid: int | None = None,
) -> None:
    """Post a note on an existing merge request."""
    if not token:
        raise ValueError(
            "--post-mr-comment requires a GitLab token "
            "(--token, GITLAB_TOKEN, or CI_JOB_TOKEN)"
        )
    resolved_iid = mr_iid
    if resolved_iid is None:
        env_iid = os.getenv("CI_MERGE_REQUEST_IID")
        if env_iid and env_iid.isdigit():
            resolved_iid = int(env_iid)
    if resolved_iid is None:
        raise ValueError("--post-mr-comment requires --mr-iid or CI_MERGE_REQUEST_IID.")

    project_path = _resolve_project_path(project)
    url = _resolve_gitlab_url(gitlab_url)
    gl = gitlab.Gitlab(url, private_token=token)
    project_obj = gl.projects.get(project_path)
    merge_request = project_obj.mergerequests.get(resolved_iid)
    merge_request.notes.create({"body": body})
    logger.info(f"Posted compliance comment on merge request !{resolved_iid}")
