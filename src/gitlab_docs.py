"""
Gitlab-Docs entrypoint to auto generate gitlab-ci documentation from yml configuration files
Author: Charlie Smith
"""

## Import Thirdparty Libraries
import os
import click
from datetime import datetime
import src.properties.includes as includes
import src.properties.jobs as jobs
import src.properties.variables as variables
import src.properties.workflows as workflows
from src.modules.logging import logger
import src.modules.doc_controller as md_writer
from src.modules.doc_controller import update_marked_block, add_between_markers

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
    "--dry-mode",
    "-d",
    "DRY_MODE",
    required=False,
    help="If set will disable documentation from being written",
    is_flag=True,
    default=False
)
@click.option(
    "--output-file",
    "-o",
    "OUTPUT_FILE",
    required=False,
    help="Output location of the markdown documentation.",

    default="README.md"
)
@click.option(
    "--input-config",
    "-i",
    "GLDOCS_CONFIG_FILE",
    required=False,
    help="The Gitlab CI Input configuration file to generated documentation from.",
    default=".gitlab-ci.yml"
)

def gitlab_docs(detailed,OUTPUT_FILE,DRY_MODE,GLDOCS_CONFIG_FILE):
    """
    A command line tool to convert your gitlab-ci yml into markdown documentation.
    """

    ENABLE_WORKFLOW_DOCUMENTATION = detailed
    logger.success("Welcome to Gitlab Docs")
    update_marked_block(file_path=OUTPUT_FILE, content="\n\n")
    bootstrap =  f"""<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-LN+7fdVzj6u52u30Kp6M/trliBMCMKTyK833zpbD+pXdCLuTusPj697FH4R/5mcr" crossorigin="anonymous">
            <h1><span class="badge text-bg-primary">GITLAB DOCS - {GLDOCS_CONFIG_FILE}</span></h1>"""
    add_between_markers(file_path=OUTPUT_FILE,content=bootstrap)
    variables.document_variables(
        GLDOCS_CONFIG_FILE=GLDOCS_CONFIG_FILE,

        DISABLE_TITLE=False,
        OUTPUT_FILE=OUTPUT_FILE,
    )
    includes.document_includes(
        GLDOCS_CONFIG_FILE=GLDOCS_CONFIG_FILE,

        DISABLE_TITLE=False,
        DISABLE_TYPE_HEADING=False,
        OUTPUT_FILE=OUTPUT_FILE,
    )
    if ENABLE_WORKFLOW_DOCUMENTATION is True:
        workflows.document_workflows(
            GLDOCS_CONFIG_FILE=GLDOCS_CONFIG_FILE,
            DISABLE_TITLE=True,
            OUTPUT_FILE=OUTPUT_FILE,
        )
    jobs.get_jobs(
        GLDOCS_CONFIG_FILE=GLDOCS_CONFIG_FILE,

        DISABLE_TITLE=False,
        DISABLE_TYPE_HEADING=False,
        OUTPUT_FILE=OUTPUT_FILE,
        detailed=detailed,
    )

    # resets markdown output file and adds GITLAB DOCS closing marker
    # md_writer.gitlab_docs_reset_writer(OUTPUT_FILE=OUTPUT_FILE, MODE="CLOSING")
    logger.info(f"Successfully generated documentation for {GLDOCS_CONFIG_FILE} here: {OUTPUT_FILE}")
if __name__ == "__main__":
    gitlab_docs(obj={})
