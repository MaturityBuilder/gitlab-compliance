import logging
import os
# Logging Setup
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GITLAB DOCS")
logger.setLevel(LOG_LEVEL)
