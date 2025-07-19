from loguru import logger
import os
import sys

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

logger.remove()
format="{level}|{time:HH:mm:ss}|{module}| {message}"
message=''
if LOG_LEVEL not in ["INFO","ERROR", "WARNING", "CRITICAL", "SUCCESS"]:
    logger.add(sys.stderr,
        level="DEBUG",
        format=f"<cyan>🐛 {format}</cyan> | "
    )
logger.add(sys.stderr,
    level="INFO",
    format=f"{format} "
)
# logger.add(sys.stderr,
#     level="INFO",
#     format=f"<green>✅ {format} </green>"
# )
# logger.add(sys.stderr,
#     level="WARNING",
#     format=f"<yellow>⚠️ {format}</yellow>"
# )
# logger.add(sys.stderr,
#     level="CRITICAL",
#     format=f"<red>🔥  {format}</red>"
# )
# logger.add(sys.stderr,
#     level="ERROR",
#     format=f"<red>❌ {format}</red>"
# )
