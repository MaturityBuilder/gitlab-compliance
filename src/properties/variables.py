import yaml

import src.modules.common as common
import src.properties.table_render as table_render
from src.modules.doc_controller import add_between_markers
from src.modules.logging import logger


def document_variables(OUTPUT_FILE, GLDOCS_CONFIG_FILE, DISABLE_TITLE):
    logger.trace("Generating Documentation for Variables")

    file = common.read_yml(GLDOCS_CONFIG_FILE)
    try:
        for data in file:
            if "variables" in data:
                variables = data["variables"]
                table_md = table_render.render_variables_table(variables)
                if not DISABLE_TITLE:
                    add_between_markers(file_path=OUTPUT_FILE, content="\n")
                add_between_markers(file_path=OUTPUT_FILE, content="\n")
                add_between_markers(file_path=OUTPUT_FILE, content="## Variables")
                add_between_markers(file_path=OUTPUT_FILE, content="\n")
                add_between_markers(file_path=OUTPUT_FILE, content=table_md)
                add_between_markers(file_path=OUTPUT_FILE, content="\n")

    except yaml.YAMLError as exc:
        logger.trace(exc)
