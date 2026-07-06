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

                if isinstance(workflow, dict) and "rules" in workflow:
                    workflow_rules = workflow["rules"]
                elif isinstance(workflow, list):
                    workflow_rules = workflow
                else:
                    workflow_rules = [workflow]

                workflow_table = common.build_dict_list_table(
                    workflow_rules,
                    row_label="Rules #",
                )
                if workflow_table is None:
                    workflow_table = common.table_design(
                        field_names=["Rules #", "Workflow Rules"]
                    )
                    for count, rule in enumerate(workflow_rules, 1):
                        workflow_table.add_row([count, common.format_value(rule)])
                logger.debug(workflow)

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
