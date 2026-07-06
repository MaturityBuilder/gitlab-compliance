"""Central logging configuration for gitlab-docs."""

import logging
import os


def configure_logging() -> logging.Logger:
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(level=level, format="%(levelname)s|%(name)s|%(message)s")
    logger = logging.getLogger("gitlab_docs")
    logger.setLevel(level)
    return logger
