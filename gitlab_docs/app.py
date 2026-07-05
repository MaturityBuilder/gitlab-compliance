"""
Gitlab-Docs entrypoint to auto generate gitlab-ci documentation from yml configuration files
Author: Charlie Smith
"""

import logging
import os
from pathlib import Path

import click

from gitlab_docs.constants import SUPPORTED_OUTPUT_FORMATS
from gitlab_docs.logging_config import configure_logging
from gitlab_docs.pipeline import generate_documentation_body
from gitlab_docs.reset_docs import write_documentation

logger = configure_logging()


def _env_flag(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _workflow_docs_enabled(detailed: bool) -> bool:
    if detailed:
        return True
    return _env_flag("ENABLE_WORKFLOW_DOCUMENTATION", False)


@click.command()
@click.option(
    "--detailed",
    is_flag=True,
    default=False,
    help="Include workflow rules and per-job rules in the documentation.",
)
@click.option(
    "--config",
    "-c",
    "config_file",
    default=None,
    help="GitLab CI config file (default: GLDOCS_CONFIG_FILE or .gitlab-ci.yml).",
)
@click.option(
    "--output",
    "-o",
    "output_file",
    default=None,
    help="Output path (default: OUTPUT_FILE or GITLAB-DOCS.md).",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(sorted(SUPPORTED_OUTPUT_FORMATS), case_sensitive=False),
    default=None,
    help="Output format (default: OUTPUT_FORMAT or markdown).",
)
def gitlab_docs(detailed, config_file, output_file, output_format):
    """Convert GitLab CI YAML into documentation (Markdown, HTML, JSON, or CSV)."""

    config_path = Path(
        config_file or os.getenv("GLDOCS_CONFIG_FILE", ".gitlab-ci.yml")
    )
    out_path = Path(output_file or os.getenv("OUTPUT_FILE", "GITLAB-DOCS.md"))
    fmt = (output_format or os.getenv("OUTPUT_FORMAT", "markdown")).lower()

    if not config_path.is_file():
        click.secho(
            f"GitLab configuration {config_path} does not exist",
            err=True,
            bold=True,
            fg="red",
        )
        raise SystemExit(1)

    include_workflows = _workflow_docs_enabled(detailed)
    click.secho(f"Parsing {config_path}", err=True, bold=True, fg="blue")

    body = generate_documentation_body(
        config_path,
        detailed=detailed,
        document_workflows=include_workflows,
        output_format=fmt,
    )

    if fmt != "markdown" and out_path.suffix.lower() in {".md", ".markdown"}:
        logger.warning(
            "Writing %s format to a Markdown filename (%s); consider a matching extension",
            fmt,
            out_path,
        )

    write_documentation(out_path, body, fmt)
    click.secho(f"Wrote documentation to {out_path} ({fmt})", fg="green")


if __name__ == "__main__":
    gitlab_docs()
