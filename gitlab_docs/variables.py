import logging
from typing import Any

from gitlab_docs.render import DocTable, render_table

logger = logging.getLogger("gitlab_docs.variables")

MISSING = "&#x274c;"


def _variable_row(name: str, raw: Any) -> list[str]:
    description = MISSING
    options = MISSING
    expand = "true"
    if isinstance(raw, str):
        value = raw
    elif isinstance(raw, dict):
        value = str(raw.get("value", raw))
        description = raw.get("description", MISSING)
        options = raw.get("options", MISSING)
        expand = str(raw.get("expand", "true"))
        if description == MISSING and "description" not in raw:
            logger.debug(
                "Variable %s has no description (GitLab CI variables should document it)",
                name,
            )
    else:
        value = str(raw)
    return [name, value, str(description), str(options), str(expand)]


def build_variables_section(data: dict, *, output_format: str = "markdown") -> str:
    variables = data.get("variables")
    if not variables or not isinstance(variables, dict):
        return ""

    table = DocTable(
        headers=["Key", "Value", "Description", "Options", "Expand"],
    )
    for name in sorted(variables):
        table.add_row(_variable_row(name, variables[name]))

    return "## Variables\n\n" + render_table(table, output_format)


def document_variables(OUTPUT_FILE, GLDOCS_CONFIG_FILE, WRITE_MODE, DISABLE_TITLE):
    """Legacy entry point; prefer pipeline.generate_documentation_body."""
    from gitlab_docs.yaml_load import load_ci_config
    from gitlab_docs.reset_docs import write_documentation

    data = load_ci_config(GLDOCS_CONFIG_FILE)
    body = build_variables_section(data)
    if body:
        write_documentation(OUTPUT_FILE, body, "markdown")
