"""Backward-compatible import path for ``src.gitlab_compliance``.

Tests and older integrations import ``src.gitlab_docs``. Patchable CLI
dependencies are defined here so monkeypatches on this module affect the
commands in ``gitlab_compliance``.
"""
