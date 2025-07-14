"""
A module for controlling inserts and updates to output files.
"""

import os
from src.modules.logging import logger

file_path = "README.md"
marker_start = "[comment]: <> (gitlab-docs-opening-auto-generated)"
marker_end = "[comment]: <> (gitlab-docs-closing-auto-generated)"
dry=os.environ.get("DRY_MODE", False)
# print(os.environ.get("DRY_MODE"))
def update_marked_block(file_path, content):
    """
    Inserts or updates a uniquely marked block in a file.

    - If the markers already exist, updates the content between them.
    - If not, appends a new marked block to the file.
    - Supports multiple distinct blocks (different marker pairs) in one file.

    Args:
        content (str): Content to insert between the markers.
        dry (bool): If True, logs intended changes but doesn't modify the file.
    """
    try:
        if not os.path.exists(file_path):
            logger.trace(f"File {file_path} does not exist. Creating new file.")
            if dry:
                logger.info("[Dry Run] Would create file and insert new block.")
                return
            with open(file_path, "w", encoding="utf-8"):
                pass  # create an empty file

        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        start_idx = end_idx = None
        for i, line in enumerate(lines):
            if marker_start in line:
                start_idx = i
            if marker_end in line and start_idx is not None:
                end_idx = i
                break

        block = [f"{marker_start}\n", content.rstrip() + "\n", f"{marker_end}\n"]

        if start_idx is not None and end_idx is not None and start_idx < end_idx:
            logger.trace("Updating existing block.")
            lines = lines[:start_idx] + block + lines[end_idx + 1 :]
        else:
            logger.trace("Appending new block.")
            if lines and not lines[-1].endswith("\n"):
                lines[-1] += "\n"
            lines += ["\n"] + block

        if dry:
            logger.info("[Dry Run] Would write the following to file:")
            logger.info("".join(lines))
        else:
            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(lines)
            logger.trace(f"Block successfully written to {file_path}")

    except Exception as e:
        logger.error(f"Failed to update block in {file_path}: {e}")


def add_between_markers(file_path, content):
    """
    Appends content between marker lines in a file.

    - If the marker block does not exist, it creates it and adds the content.
    - If the marker block exists, it inserts the content before the end marker.
    - Creates the file if it doesn't exist.

    Args:
        content (str): Content to insert between the markers.
        dry (bool): If True, logs intended changes but doesn't modify the file.
    """
    try:
        if not os.path.exists(file_path):
            logger.trace(f"File {file_path} does not exist. Creating new file with block.")
            if dry:
                logger.info("[Dry Run] Would create file with content:")
                logger.info(f"{marker_start}\n{content.rstrip()}\n{marker_end}")
                return
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"{marker_start}\n{content.rstrip()}\n{marker_end}\n")
            return

        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        start_idx = end_idx = None
        for i, line in enumerate(lines):
            if marker_start in line:
                start_idx = i
            elif marker_end in line and start_idx is not None:
                end_idx = i
                break

        if start_idx is not None and end_idx is not None:
            logger.trace("Inserting content before existing end marker.")
            insertion_point = end_idx
            lines = (
                lines[:insertion_point]
                + [content.rstrip() + "\n"]
                + lines[insertion_point:]
            )
        else:
            logger.trace("Appending new marker block.")
            if lines and not lines[-1].endswith("\n"):
                lines[-1] += "\n"
            lines += ["\n", marker_start + "\n", content.rstrip() + "\n", marker_end + "\n"]

        if dry:
            logger.logger("[Dry Run] Would write the following to file:")
            logger.logger("".join(lines))
        else:
            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(lines)
            logger.trace(f"Content successfully added to {file_path}")
    except Exception as e:
            logger.error(f"Failed to insert content into {file_path}: {e}")
