"""
This module is a code quality engine to detect poor forms in yaml and replace them before parsing.
"""
from logging import logger
def yml_tab_check():
    logger.info("Checking for \t in yaml files before generating document")
