import logging
import os
import yaml
import src.modules.common as common
from src.modules.logging import logger
# from src.modules.doc_controller import update_marked_block
from src.modules.doc_controller import add_between_markers

def document_variables(OUTPUT_FILE, GLDOCS_CONFIG_FILE,  DISABLE_TITLE):
    logger.trace("Generating Documentation for Variables")

    from prettytable import MARKDOWN
    with open(GLDOCS_CONFIG_FILE, "r") as file:
        try:
            data = yaml.load(file, Loader=common.EnvLoader)
            if "variables" in data:
                variables = data["variables"]
                # logger.trace(gldocs.generate_markdown_table(variables))
                from prettytable import PrettyTable

                variables_table = PrettyTable()
                variables_table.set_style(MARKDOWN)
                variables_table.field_names = [
                    "Key",
                    "Value",
                    "Description",
                    "Options",
                    "Expand",
                ]
                # variables_table.add_rows([variables])
                # logger.trace(variables)

                for v in variables:
                    description = "&#x274c;"
                    options = "&#x274c;"
                    expand = "true"
                    result = {}
                    if type(variables[v]) is str:
                        logger.debug("Simple variable found: " + variables[v])
                        result["value"] = variables[v]

                    else:
                        if "description" in variables[v]:
                            description = variables[v]["description"]
                        else:
                            logger.debug(
                                "Description for: "
                                + v
                                + " isn't set, variable should have description set, "
                                + "gitlab-docs considers this malformed :("
                            )
                            description = "&#x274c;"

                        if "options" in variables[v]:
                            options = variables[v]["options"]
                        else:
                            options = "&#x274c;"
                        if "expand" in variables[v]:
                            expand = variables[v]["expand"]
                        else:
                            logger.debug(
                                "expand key: "
                                + v
                                + " isn't set, default value will recored as 'true'"
                                + "https://docs.gitlab.com/ee/ci/yaml/#variablesexpand"
                            )
                            expand = "true"

                variables_table.add_row([v, variables[v], description, options, expand])

                # f = open(OUTPUT_FILE, WRITE_MODE)
                if not DISABLE_TITLE:
                    # GLDOCS_CONFIG_FILE_HEADING = str("## " + GLDOCS_CONFIG_FILE + "\n\n")
                    add_between_markers(file_path=OUTPUT_FILE, content="\n")
                    # add_between_markers(file_path=OUTPUT_FILE, content=GLDOCS_CONFIG_FILE_HEADING)
                add_between_markers(file_path=OUTPUT_FILE, content="\n")
                add_between_markers(file_path=OUTPUT_FILE, content="## Variables")
                add_between_markers(file_path=OUTPUT_FILE, content="\n")
                add_between_markers(file_path=OUTPUT_FILE, content=str(variables_table))
                add_between_markers(file_path=OUTPUT_FILE, content="\n")
                # f.close()

        except yaml.YAMLError as exc:
            logger.trace(exc)
