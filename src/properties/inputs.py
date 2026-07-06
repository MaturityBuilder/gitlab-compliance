import logging
import os
import yaml
import src.modules.common as common
from src.modules.logging import logger
# from src.modules.doc_controller import add_between_markers
from src.modules.doc_controller import add_between_markers

def document_inputs(OUTPUT_FILE, GLDOCS_CONFIG_FILE,  DISABLE_TITLE):
    logger.trace("Generating Documentation for inputs")

    

    file = common.read_yml(GLDOCS_CONFIG_FILE)
    try:
        for data in file:
            if "spec" in data:
                inputs = data["spec"]["inputs"]
                # logger.trace(gldocs.generate_markdown_table(inputs))
            
                inputs_table = common.table_design(headers=[
                    "Key",
                    "Value",
                    "Description",
                    "Options",
                    "Expand",
                ])
                # inputs_table.add_rows([inputs])
                logger.info(inputs)

                for v in inputs:
                    description = "&#x274c;"
                    options = "&#x274c;"
                    expand = "true"
                    result = {}
                    if type(inputs[v]) is str:
                        logger.debug("Simple input found: " + inputs[v])
                        result["value"] = inputs[v]

                    else:
                        if "description" in inputs[v]:
                            description = inputs[v]["description"]
                        else:
                            logger.debug(
                                "Description for: "
                                + v
                                + " isn't set, input should have description set, "
                                + "gitlab-docs considers this malformed :("
                            )
                            description = "&#x274c;"

                        if "options" in inputs[v]:
                            options = inputs[v]["options"]
                        else:
                            options = "&#x274c;"
                        if "expand" in inputs[v]:
                            expand = inputs[v]["expand"]
                        else:
                            logger.debug(
                                "expand key: "
                                + v
                                + " isn't set, default value will recored as 'true'"
                                + "https://docs.gitlab.com/ee/ci/yaml/#inputsexpand"
                            )
                            expand = "true"

                    inputs_table.add_row([v, inputs[v], description, options, expand])

                # f = open(OUTPUT_FILE, WRITE_MODE)
                if not DISABLE_TITLE:
                    # GLDOCS_CONFIG_FILE_HEADING = str("## " + GLDOCS_CONFIG_FILE + "\n\n")
                    add_between_markers(file_path=OUTPUT_FILE, content="\n")
                    # add_between_markers(file_path=OUTPUT_FILE, content=GLDOCS_CONFIG_FILE_HEADING)
                add_between_markers(file_path=OUTPUT_FILE, content="\n")
                add_between_markers(file_path=OUTPUT_FILE, content="## Inputs")
                add_between_markers(file_path=OUTPUT_FILE, content="\n")
                add_between_markers(file_path=OUTPUT_FILE, content=str(inputs_table))
                add_between_markers(file_path=OUTPUT_FILE, content="\n")
                # f.close()

    except yaml.YAMLError as exc:
        logger.trace(exc)
