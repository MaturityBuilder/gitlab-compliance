"""
Gitlab-Docs entrypoint to auto generate gitlab-ci documentation from yml configuration files
Author: Charlie Smith
"""

## Import Thirdparty Libraries
import logging, os
from datetime import datetime, timedelta
from distutils.util import strtobool
import time
import modules.includes as includes
import modules.variables as variables
import modules.reset_docs as md_writer
import modules.jobs as jobs
# flake8: noqa: E501
# Logging Setup
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GITLAB DOCS")
logger.setLevel(LOG_LEVEL)

print("Welcome to Gitlab Docs")
# resets markdown output file and adds GITLAB DOCS opening marker

md_writer.gitlab_docs_reset_writer(OUTPUT_FILE="/gitlab-project/GITLAB_CONFIGURATION.md", MODE="STARTING")

includes.document_includes(GLDOCS_CONFIG_FILE="/gitlab-project/.gitlab-ci.yml",WRITE_MODE="w")
# variables.document_variables(GLDOCS_CONFIG_FILE="/gitlab-project/.gitlab-ci.yml",WRITE_MODE="a")
# jobs.get_jobs(GLDOCS_CONFIG_FILE="/gitlab-project/.gitlab-ci.yml",WRITE_MODE="a")


# resets markdown output file and adds GITLAB DOCS closing marker
md_writer.gitlab_docs_reset_writer(OUTPUT_FILE="/gitlab-project/GITLAB_CONFIGURATION.md", MODE="CLOSING")