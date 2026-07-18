"""Redact secrets before logging or posting to GitLab MR comments/descriptions."""

from __future__ import annotations

import os
import re

REDACTED = "***"

# Exact values from these env vars (when long enough) are scrubbed from text.
_SECRET_ENV_KEYS = (
    "GITLAB_TOKEN",
    "CI_JOB_TOKEN",
    "PRIVATE_TOKEN",
    "GITLAB_PRIVATE_TOKEN",
    "GITHUB_TOKEN",
    "GH_TOKEN",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_SESSION_TOKEN",
    "NPM_TOKEN",
    "PYPI_TOKEN",
    "DOCKER_PASSWORD",
    "REGISTRY_PASSWORD",
)

_MIN_ENV_SECRET_LEN = 8

# GitLab / common token prefixes and URL credential forms.
_TOKEN_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bglpat-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bgldt-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bglrt-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bglptt-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bglsoat-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._\-+=/]{16,}"),
    re.compile(
        r"(?i)(private_token|access_token|api_token|password|secret|token)"
        r"([=:])\s*([^\s&\"']{8,})"
    ),
)


def _env_secret_values() -> list[str]:
    values: list[str] = []
    seen: set[str] = set()
    for key in _SECRET_ENV_KEYS:
        raw = os.getenv(key)
        if not raw:
            continue
        value = raw.strip()
        if len(value) < _MIN_ENV_SECRET_LEN:
            continue
        if value in seen:
            continue
        seen.add(value)
        values.append(value)
    # Longest first so overlapping substrings redact fully.
    values.sort(key=len, reverse=True)
    return values


def redact_secrets(text: str | None) -> str:
    """Return ``text`` with known env secrets and common token patterns masked."""
    if text is None:
        return ""
    if not text:
        return text

    redacted = text
    for value in _env_secret_values():
        if value in redacted:
            redacted = redacted.replace(value, REDACTED)

    for pattern in _TOKEN_PATTERNS:
        if pattern.groups:
            redacted = pattern.sub(
                lambda match: f"{match.group(1)}{match.group(2)}{REDACTED}",
                redacted,
            )
        else:
            redacted = pattern.sub(REDACTED, redacted)
    return redacted


def token_is_ci_job_token(token: str) -> bool:
    """True when ``token`` is exactly the current ``CI_JOB_TOKEN`` value."""
    job_token = (os.getenv("CI_JOB_TOKEN") or "").strip()
    return bool(job_token) and token == job_token
