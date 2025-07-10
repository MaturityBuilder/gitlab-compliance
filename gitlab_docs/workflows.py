# import gitlab_docs.yaml_md_table as gldocs
import logging
import os
import yaml
import gitlab_docs.common as common

# from pytablewriter import MarkdownTableWriter
from prettytable import MARKDOWN

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GITLAB DOCS|INCLUDES WRAPPER")
logger.setLevel(LOG_LEVEL)


def document_workflows(
    OUTPUT_FILE, GLDOCS_CONFIG_FILE, WRITE_MODE="a", DISABLE_TITLE=False
):
    print("Generating Documentation for Workflows")

    with open(GLDOCS_CONFIG_FILE, "r") as file:
        try:
            data = yaml.load(file, Loader=common.EnvLoader)
            if "workflow" in data:
                workflow = data["workflow"]

                # print(gldocs.generate_markdown_table(includes))
                from prettytable import PrettyTable

                workflow_table = PrettyTable()
                workflow_table.set_style(MARKDOWN)
                workflow_table.field_names = ["Rules #", "Workflow Rules"]
                # workflow_table.add_rows([includes])
                logger.debug(workflow)
                count = 0
                for w in workflow:
                    count = count + 1
                    # print("count: " + str(count))
                    # if isinstance(w, (str)):
                    value = str(w).replace("{", "").replace("}", "")
                    print(value)
                    workflow_table.add_row([count, str(value)])

                f = open(OUTPUT_FILE, "a")
                if not DISABLE_TITLE:
                    GLDOCS_CONFIG_FILE_HEADING = str(
                        "## " + GLDOCS_CONFIG_FILE + "\n\n"
                    )
                    f.write("\n")
                    f.write(GLDOCS_CONFIG_FILE_HEADING)
                f.write(str(workflow_table))
                f.close()
                logger.debug("")
                logger.debug(str(workflow_table))
                logger.debug("")
        except yaml.YAMLError as exc:
            print(exc)
