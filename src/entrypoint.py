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
# flake8: noqa: E501
print("Welcome to Gitlab Docs")

includes.document_includes(GLDOCS_CONFIG_FILE="/gitlab-project/.gitlab-ci.yml",WRITE_MODE="w")
