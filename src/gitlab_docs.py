"""
Gitlab-Docs entrypoint to auto generate gitlab-ci documentation from yml configuration files
Author: Charlie Smith
"""

## Import Thirdparty Libraries
import os
import click
import src.properties.includes as includes
import src.properties.jobs as jobs
import src.properties.variables as variables
import src.properties.workflows as workflows
from src.modules.logging import logger
import src.modules.reset_docs as md_writer

# flake8: noqa: E501


# ENABLE_WORKFLOW_DOCUMENTATION = os.getenv("ENABLE_WORKFLOW_DOCUMENTATION", False)
@click.command()
@click.option(
    "--detailed",
    required=False,
    help="Will include workflow and rules from jobs.",
    is_flag=True,
    default=False
)
@click.option(
    "--output-file",
    "-o",
    "OUTPUT_FILE",
    required=False,
    help="Output location of the markdown documentation.",

    default="GITLAB-DOCS.md"
)
def gitlab_docs(detailed,OUTPUT_FILE):
    """A command line tool to convert your gitlab-ci yml into markdown documentation."""

    ENABLE_WORKFLOW_DOCUMENTATION = detailed
    logger.success("Welcome to Gitlab Docs")
    # resets markdown output file and adds GITLAB DOCS opening marker
    GLDOCS_CONFIG_FILE = os.getenv("GLDOCS_CONFIG_FILE", ".gitlab-ci.yml")
    try:
        sudoku = open(GLDOCS_CONFIG_FILE, "r").readlines()
    except FileNotFoundError:
        click.error(f"Gitlab Configuration {GLDOCS_CONFIG_FILE} doesn't exist", err=True, blink=True, bold=True, fg="red")
        exit(1)
    else:
        # md_writer.gitlab_docs_reset_writer(OUTPUT_FILE=OUTPUT_FILE, MODE="STARTING")
        variables.document_variables(
            GLDOCS_CONFIG_FILE=GLDOCS_CONFIG_FILE,
            WRITE_MODE="w",
            DISABLE_TITLE=False,
            OUTPUT_FILE=OUTPUT_FILE,
        )
        includes.document_includes(
            GLDOCS_CONFIG_FILE=GLDOCS_CONFIG_FILE,
            WRITE_MODE="w",
            DISABLE_TITLE=False,
            DISABLE_TYPE_HEADING=False,
            OUTPUT_FILE=OUTPUT_FILE,
        )
        if ENABLE_WORKFLOW_DOCUMENTATION is True:
            workflows.document_workflows(
                GLDOCS_CONFIG_FILE=GLDOCS_CONFIG_FILE,
                WRITE_MODE="w",
                DISABLE_TITLE=True,
                OUTPUT_FILE=OUTPUT_FILE,
            )
        jobs.get_jobs(
            GLDOCS_CONFIG_FILE=GLDOCS_CONFIG_FILE,
            WRITE_MODE="w",
            DISABLE_TITLE=False,
            DISABLE_TYPE_HEADING=False,
            OUTPUT_FILE=OUTPUT_FILE,
            detailed=detailed,
        )

        # resets markdown output file and adds GITLAB DOCS closing marker
        md_writer.gitlab_docs_reset_writer(OUTPUT_FILE=OUTPUT_FILE, MODE="CLOSING")
    logger.info(f"Successfully generated documentation for {GLDOCS_CONFIG_FILE} here: {OUTPUT_FILE}")
if __name__ == "__main__":
    gitlab_docs(obj={})
