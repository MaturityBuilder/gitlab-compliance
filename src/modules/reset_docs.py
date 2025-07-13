import os
from src.modules.logging import logger
file_path="README.md"

marker_start="[comment]: <> (gitlab-docs-opening-auto-generated)"
marker_end="[comment]: <> (gitlab-docs-closing-auto-generated)"
gldocs_opening = "[comment]: <> (gitlab-docs-opening-auto-generated)"
gldocs_closing = "[comment]: <> (gitlab-docs-closing-auto-generated)"

def update_marked_block(new_content):
    """
    Inserts or updates a uniquely marked block in a file.

    - If the markers already exist, updates the content between them.
    - If not, appends a new marked block to the file.
    - Supports multiple distinct blocks (different marker pairs) in one file.

    Args:
        file_path (str): Path to the file to modify.
        marker_start (str): Unique start marker (e.g., '# BEGIN_GITLAB_DOCS').
        marker_end (str): Unique end marker (e.g., '# END_GITLAB_DOCS').
        new_content (str): Content to insert between the markers.
    """
    # file_path, marker_start, marker_end,
    # file_path="GITLAB-DOCS.md"
    # marker_start="# BEGIN_GITLAB_DOCS"
    # marker_end="# END_GITLAB_DOCS"
    # Create the file if it doesn't exist
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            pass  # create an empty file
    # Read the file contents
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    start_idx = end_idx = None
    for i, line in enumerate(lines):
        if marker_start in line:
            start_idx = i
        if marker_end in line and start_idx is not None:
            end_idx = i
            break

    # Construct the block
    block = [f"{marker_start}\n", new_content.rstrip() + "\n", f"{marker_end}\n"]

    if start_idx is not None and end_idx is not None and start_idx < end_idx:
        # Update existing block
        lines = lines[:start_idx] + block + lines[end_idx + 1 :]
    else:
        # Append new block
        if lines and not lines[-1].endswith("\n"):
            lines[-1] += "\n"
        lines += ["\n"] + block

    # Write back the updated file
    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

def add_between_markers(new_content):
    """
    Appends content between marker lines in a file.

    - If the marker block does not exist, it creates it and adds the content.
    - If the marker block exists, it inserts the content before the end marker.
    - Creates the file if it doesn't exist.

    Args:
        file_path (str): File to modify.
        marker_start (str): Unique start marker (e.g., '# BEGIN_DOCS').
        marker_end (str): Unique end marker (e.g., '# END_DOCS').
        new_content (str): Content to insert between the markers.
    """
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"{marker_start}\n{new_content.rstrip()}\n{marker_end}\n")
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
        # Insert before the end marker
        insertion_point = end_idx
        lines = (
            lines[:insertion_point]
            + [new_content.rstrip() + "\n"]
            + lines[insertion_point:]
        )
    else:
        # Append whole block
        if lines and not lines[-1].endswith("\n"):
            lines[-1] += "\n"
        lines += ["\n", marker_start + "\n", new_content.rstrip() + "\n", marker_end + "\n"]

    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(lines)
