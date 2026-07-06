import logging
from typing import Any

import semver

from src.modules.constants import NON_SEMVER_REFS
from src.modules.render import DocTable, render_table

logger = logging.getLogger("gitlab_docs.workflows")


def _workflow_rule_entries(workflow: Any) -> list[Any]:
    if workflow is None:
        return []
    if isinstance(workflow, list):
        return workflow
    if isinstance(workflow, dict):
        if "rules" in workflow and isinstance(workflow["rules"], list):
            return workflow["rules"]
        return [workflow]
    return [workflow]


def build_workflows_section(data: dict, *, output_format: str = "markdown") -> str:
    if "workflow" not in data:
        return ""

    rules = _workflow_rule_entries(data["workflow"])
    if not rules:
        return ""

    table = DocTable(headers=["Rules #", "Workflow Rules"])
    for index, rule in enumerate(rules, start=1):
        value = str(rule).replace("{", "").replace("}", "")
        table.add_row([str(index), value])

    return "## Workflow\n\n" + render_table(table, output_format)


def document_workflows(
    OUTPUT_FILE, GLDOCS_CONFIG_FILE, WRITE_MODE="a", DISABLE_TITLE=False
):
    from src.modules.reset_docs import write_documentation
    from src.modules.yaml_load import load_ci_config

    data = load_ci_config(GLDOCS_CONFIG_FILE)
    body = build_workflows_section(data)
    if body:
        write_documentation(OUTPUT_FILE, body, "markdown")
