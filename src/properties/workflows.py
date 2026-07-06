# import gitlab_docs.yaml_md_table as gldocs
import logging
import os
import yaml
import src.modules.common as common
from src.modules.logging import logger
from src.modules.doc_controller import add_between_markers


def document_workflows(
    OUTPUT_FILE, GLDOCS_CONFIG_FILE,  DISABLE_TITLE=False
):
    logger.trace("Generating Documentation for Workflows")
    file = common.read_yml(GLDOCS_CONFIG_FILE)
    try:
        for data in file:
            if "workflow" in data:
                workflow = data["workflow"]

                workflow_table = common.table_design(field_names = ["Rules #", "Workflow Rules"])
                logger.debug(workflow)
                count = 0
                for w in workflow:
                    count = count + 1
                    # logger.trace("count: " + str(count))
                    # if isinstance(w, (str)):
                    value = str(w).replace("{", "").replace("}", "")
                    logger.trace(value)
                    workflow_table.add_row([count, str(value)])

                # f = open(OUTPUT_FILE, "a")
                if not DISABLE_TITLE:
                    GLDOCS_CONFIG_FILE_HEADING = str(
                        "## " + GLDOCS_CONFIG_FILE + "\n\n"
                    )
                    add_between_markers(file_path=OUTPUT_FILE, content="\n")
                    add_between_markers(file_path=OUTPUT_FILE, content=GLDOCS_CONFIG_FILE_HEADING)
                add_between_markers(file_path=OUTPUT_FILE, content=str(workflow_table))
                # f.close()
                logger.debug("")
                logger.debug(str(workflow_table))
                logger.debug("")
    except yaml.YAMLError as exc:
        logger.trace(exc)
