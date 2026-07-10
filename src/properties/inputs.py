import yaml

import src.modules.common as common
import src.properties.table_render as table_render
from src.modules.doc_controller import add_between_markers
from src.modules.logging import logger


def document_inputs(OUTPUT_FILE, GLDOCS_CONFIG_FILE, DISABLE_TITLE):
    logger.trace("Generating Documentation for inputs")

    file = common.read_yml(GLDOCS_CONFIG_FILE)
    try:
        for data in file:
            if "spec" in data:
                inputs = data["spec"]["inputs"]
                logger.info(inputs)
                table_md = table_render.render_inputs_table(inputs)
                if not DISABLE_TITLE:
                    add_between_markers(file_path=OUTPUT_FILE, content="\n")
                add_between_markers(file_path=OUTPUT_FILE, content="\n")
                add_between_markers(file_path=OUTPUT_FILE, content="## Inputs")
                add_between_markers(file_path=OUTPUT_FILE, content="\n")
                add_between_markers(file_path=OUTPUT_FILE, content=table_md)
                add_between_markers(file_path=OUTPUT_FILE, content="\n")

    except yaml.YAMLError as exc:
        logger.trace(exc)
