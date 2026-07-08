"""Bundled compliance policies shipped with gitlab-compliance."""

from __future__ import annotations

import os

BUILTIN_POLICIES_DIR = os.path.join(os.path.dirname(__file__))

__all__ = ["BUILTIN_POLICIES_DIR"]
