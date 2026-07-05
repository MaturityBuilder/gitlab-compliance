import logging
from pathlib import Path
from typing import Any

from gitlab_docs.constants import RESERVED_CI_KEYS
from gitlab_docs.render import DocTable, render_table

logger = logging.getLogger("gitlab_docs.jobs")


def _format_job_value(value: Any) -> str:
    return (
        str(value)
        .replace(",", "\n")
        .replace("{", "")
        .replace("}", "")
    )


def _job_block(
    job_name: str,
    job_config: dict,
    *,
    output_format: str,
    detailed: bool,
) -> str:
    config = dict(job_config)
    if not detailed:
        config.pop("rules", None)
    config.pop("before_script", None)
    config.pop("script", None)
    config.pop("after_script", None)

    if not config:
        return ""

    table = DocTable(headers=["**Key**", "**Value**"])
    for key in sorted(config):
        table.add_row([f"**{key}**", _format_job_value(config[key])])

    title = f"### {job_name.upper()}\n\n"
    return title + render_table(table, output_format)


def build_jobs_section(
    config_file: Path,
    data: dict | None = None,
    *,
    output_format: str = "markdown",
    detailed: bool = False,
    disable_title: bool = False,
    disable_type_heading: bool = False,
) -> str:
    from gitlab_docs.yaml_load import load_ci_config

    if data is None:
        data = load_ci_config(config_file)

    parts: list[str] = []
    if not disable_title:
        parts.append(f"## {config_file}\n")
    if not disable_type_heading:
        parts.append("## Jobs\n")

    for key, value in data.items():
        if key in RESERVED_CI_KEYS:
            logger.debug("Skipping reserved GitLab CI key: %s", key)
            continue
        if not isinstance(value, dict):
            logger.warning(
                "Skipping key %s in %s: expected a job mapping, got %s",
                key,
                config_file,
                type(value).__name__,
            )
            continue
        block = _job_block(key, value, output_format=output_format, detailed=detailed)
        if block:
            parts.append(block)

    return "\n".join(part for part in parts if part).strip()


def get_jobs(
    OUTPUT_FILE,
    GLDOCS_CONFIG_FILE,
    WRITE_MODE,
    DISABLE_TITLE=True,
    DISABLE_TYPE_HEADING=True,
    detailed=False,
    experimental=False,
):
    from gitlab_docs.reset_docs import write_documentation

    body = build_jobs_section(
        Path(GLDOCS_CONFIG_FILE),
        output_format="markdown",
        detailed=detailed,
        disable_title=not DISABLE_TITLE,
        disable_type_heading=not DISABLE_TYPE_HEADING,
    )
    if body:
        write_documentation(OUTPUT_FILE, body, "markdown")
