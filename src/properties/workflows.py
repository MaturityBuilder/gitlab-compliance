# import gitlab_docs.yaml_md_table as gldocs
import logging
import os
import yaml
import src.modules.common as common
from src.modules.logging import logger
# from pytablewriter import MarkdownTableWriter
from prettytable import MARKDOWN
from src.modules.doc_controller import add_between_markers


def document_workflows(
    OUTPUT_FILE, GLDOCS_CONFIG_FILE,  DISABLE_TITLE=False
):
    logger.trace("Generating Documentation for Workflows")

    with open(GLDOCS_CONFIG_FILE, "r") as file:
        try:
            data = yaml.load(file, Loader=common.EnvLoader)
            if "workflow" in data:
                workflow = data["workflow"]

                # logger.trace(gldocs.generate_markdown_table(includes))
                from prettytable import PrettyTable

                workflow_table = PrettyTable()
                workflow_table.set_style(MARKDOWN)
                workflow_table.field_names = ["Rules #", "Workflow Rules"]
                # workflow_table.add_rows([includes])
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
                    add_between_markers("\n")
                    add_between_markers(GLDOCS_CONFIG_FILE_HEADING)
                add_between_markers(str(workflow_table))
                # f.close()
                logger.debug("")
                logger.debug(str(workflow_table))
                logger.debug("")
        except yaml.YAMLError as exc:
            logger.trace(exc)
