"""Load GitLab CI YAML with gitlab-docs customisations."""

from pathlib import Path
from typing import Any

import yaml

import src.modules.common as common


def load_ci_config(path: str | Path) -> dict[str, Any]:
    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as handle:
        data = yaml.load(handle, Loader=common.EnvLoader)
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError(f"GitLab CI config must be a mapping at root: {config_path}")
    return data
