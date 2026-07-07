"""Backward-compatible import path for ``src.gitlab_compliance``.

Tests and older integrations import ``src.gitlab_docs``. Patchable CLI
dependencies are defined here so monkeypatches on this module affect the
commands in ``gitlab_compliance``.
"""

from src.compliance.metadata import build_policy_catalog
from src.compliance.oci_registry import (
    DEFAULT_POLICY_DIR,
    is_oci_reference,
    pull_policies,
    push_policies,
    resolve_features_dir,
)
from src.compliance.render import render_compliance_report
from src.compliance.runner import run_compliance

__all__ = [
    "DEFAULT_POLICY_DIR",
    "build_policy_catalog",
    "is_oci_reference",
    "pull_policies",
    "push_policies",
    "render_compliance_report",
    "resolve_features_dir",
    "run_compliance",
]


def __getattr__(name: str):
    import src.gitlab_compliance as mod

    return getattr(mod, name)


def __dir__():
    import src.gitlab_compliance as mod

    return sorted(set(__all__) | set(dir(mod)))
