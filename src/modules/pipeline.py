"""Build full documentation body from a GitLab CI configuration file."""

from __future__ import annotations

import logging
from pathlib import Path

from src.modules.yaml_load import load_ci_config
from src.properties.sections import includes, jobs, variables, workflows

logger = logging.getLogger("gitlab_docs.pipeline")


def generate_documentation_body(
    config_file: str | Path,
    *,
    detailed: bool = False,
    document_workflows: bool = False,
    output_format: str = "markdown",
) -> str:
    config_path = Path(config_file)
    data = load_ci_config(config_path)
    sections: list[str] = []

    variables_part = variables.build_variables_section(
        data, output_format=output_format
    )
    if variables_part:
        sections.append(variables_part)

    includes_part = includes.build_includes_section(
        config_path,
        data,
        output_format=output_format,
        disable_type_heading=False,
    )
    if includes_part:
        sections.append(includes_part)

    if document_workflows:
        workflows_part = workflows.build_workflows_section(
            data, output_format=output_format
        )
        if workflows_part:
            sections.append(workflows_part)

    jobs_part = jobs.build_jobs_section(
        config_path,
        data,
        output_format=output_format,
        detailed=detailed,
        disable_title=False,
        disable_type_heading=False,
    )
    if jobs_part:
        sections.append(jobs_part)

    return "\n".join(section for section in sections if section).strip()
