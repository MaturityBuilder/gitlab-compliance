import logging
import os

import yaml
import gitlab_docs.common as common
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GITLAB DOCS|VARIABLES WRAPPER")
logger.setLevel(LOG_LEVEL)

def document_variables(OUTPUT_FILE, GLDOCS_CONFIG_FILE, WRITE_MODE, DISABLE_TITLE):
    print("Generating Documentation for Variables")

    from prettytable import MARKDOWN
    with open(GLDOCS_CONFIG_FILE, "r") as file:
        try:
            data = yaml.load(file, Loader=common.EnvLoader)
            if "variables" in data:
                variables = data["variables"]
                # print(gldocs.generate_markdown_table(variables))
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
                # print(variables)

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
                            # print(
                            #     "options key: "
                            #     + v
                            #     + " isn't set, but will improve code hygiene if you"
                            #     + " set where possible, gitlab-docs  - "
                            #     + "https://docs.gitlab.com/ee/ci/yaml/"
                            #     + "#variablesoptions"
                            # )
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

                print("")
                # print(str(variables_table))
                print("")
                f = open(OUTPUT_FILE, WRITE_MODE)
                if not DISABLE_TITLE:
                    # GLDOCS_CONFIG_FILE_HEADING = str("## " + GLDOCS_CONFIG_FILE + "\n\n")
                    f.write("\n")
                    # f.write(GLDOCS_CONFIG_FILE_HEADING)
                f.write("\n")
                f.write("## Variables")
                f.write("\n")
                f.write(str(variables_table))
                f.write("\n")
                f.close()

        except yaml.YAMLError as exc:
            print(exc)
