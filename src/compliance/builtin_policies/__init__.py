"""Bundled compliance policies shipped with gitlab-compliance."""

from __future__ import annotations

import os

BUILTIN_POLICIES_DIR = os.path.join(os.path.dirname(__file__))
BUILTIN_SHELL_POLICIES_DIR = os.path.join(BUILTIN_POLICIES_DIR, "shell")
BUILTIN_SUPPLY_CHAIN_POLICIES_DIR = os.path.join(
    BUILTIN_POLICIES_DIR, "supply-chain"
)

__all__ = [
    "BUILTIN_POLICIES_DIR",
    "BUILTIN_SHELL_POLICIES_DIR",
    "BUILTIN_SUPPLY_CHAIN_POLICIES_DIR",
]
