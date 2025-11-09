from loguru import logger
import os
import sys

def configure_logger(log_level=None, output=None):
    """
    Configures Loguru logger.

    Args:
        log_level (str, optional): Log level to use. Defaults to env LOG_LEVEL or INFO.
        output (file-like, optional): Stream to write logs to. Defaults to sys.stderr.
    """
    # Remove existing sinks
    logger.remove()

    # Determine log level
    LOG_LEVEL = (log_level or os.getenv("LOG_LEVEL", "INFO")).upper()

    # Default output
    out = output or sys.stderr

    fmt = "{level}|{time:HH:mm:ss}|{module}| {message}"

    # Add DEBUG sink if LOG_LEVEL is invalid
    if LOG_LEVEL not in ["INFO", "ERROR", "WARNING", "CRITICAL", "SUCCESS"]:
        logger.add(out,
                   level="DEBUG",
                   format=f"<cyan>🐛 {fmt}</cyan> | ")

    # Always add INFO sink
    logger.add(out,
               level="INFO",
               format=f"{fmt} ")

    return logger

logger = configure_logger()