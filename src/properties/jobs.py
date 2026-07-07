import json
import os

import yaml
from prettytable import MARKDOWN
from prettytable import MARKDOWN as DESIGN
from prettytable import PrettyTable
from prettytable.colortable import ColorTable, Themes

import src.modules.common as common
from src.modules.doc_controller import add_between_markers
from src.modules.logging import logger


def get_jobs(
    OUTPUT_FILE,
    GLDOCS_CONFIG_FILE,
    DISABLE_TITLE=True,
    DISABLE_TYPE_HEADING=True,
    detailed=False,
    experimental=False,
):
    exclude_keywords = [
        "default",
        "include",
        "stages",
        "variables",
        "workflow",
        "image",
        "spec",
    ]
    logger.trace("Generating Documentation for Jobs")

    file = common.read_yml(GLDOCS_CONFIG_FILE)
    add_between_markers(file_path=OUTPUT_FILE, content="## Jobs")
    for jobs in file:
        # Create file lock against output md file
        # f = open(OUTPUT_FILE, "a")
        # if not DISABLE_TITLE:
        #     add_between_markers(file_path=OUTPUT_FILE, content="\n")
        #     GLDOCS_CONFIG_FILE_HEADING = str("## " + GLDOCS_CONFIG_FILE + "\n")
        #     add_between_markers(file_path=OUTPUT_FILE, content=GLDOCS_CONFIG_FILE_HEADING)
        # if not DISABLE_TYPE_HEADING:
        # add_between_markers(file_path=OUTPUT_FILE, content="\n")
        # add_between_markers(file_path=OUTPUT_FILE, content=str("## " + "Jobs" + "\n"))
        # add_between_markers(file_path=OUTPUT_FILE, content="\n")

        # logger.trace(type(jobs))

        for j in jobs:
            if j in exclude_keywords and not j.startswith("."):
                logger.debug("Key is reserved for gitlab: " + j)
            else:
                # Build Row Level Table to store each job config in

                job_config_table = common.table_design(
                    headers=["**Attribute**", "**Value**"]
                )
                variable_table = common.table_design(
                    headers=[
                        '<span class="badge text-bg-danger">Attribute</span>',
                        '<span class="badge text-bg-warning">Key</span>',
                        '<span class="badge text-bg-success">Value</span>',
                    ]
                )
                rules_table = None
                try:
                    if experimental is True:
                        if detailed is True and jobs[j].get("rules"):
                            jobs[j].pop("rules", None)
                    jobs[j].pop("before_script", None)
                    jobs[j].pop("script", None)
                    jobs[j].pop("after_script", None)
                    jobs[j].pop("artifacts", None)
                    # logger.trace(jobs[j])
                    job_config = []
                    value_counter = 0
                    if jobs[j]:
                        for key in sorted(jobs[j]):
                            job_Attribute = "**" + key + "**"
                            attribute_value = jobs[j][key]
                            # job_config_table_headers.append(key)
                            if key == "rules" and isinstance(attribute_value, list):
                                rules_table = common.build_dict_list_table(
                                    attribute_value
                                )
                            elif key in ["variables"]:
                                # print(json.dumps(jobs[j]["variables"].keys()))
                                # print(key)
                                var = attribute_value.keys()
                                # print(var)
                                # var=json.dumps(jobs[j][key])
                                # # .iteritems()
                                for item_key in var:
                                    value = attribute_value[item_key]
                                    value_counter = value_counter + 1
                                    variable_table.add_row([key, item_key, value])
                            elif key == "artifacts" and isinstance(attribute_value, dict):
                                var = attribute_value.keys()
                                for item_key in var:
                                    value = attribute_value[item_key]
                                    value_counter = value_counter + 1
                                    variable_table.add_row([key, item_key, value])
                            elif key in ["needs"]:
                                # print("found extends")
                                # logger.warning(len(jobs[j][key]))
                                for x in attribute_value:
                                    value_counter = value_counter + 1
                                    # print([key,"Hidden Job", x])
                                    variable_table.add_row([key, "", x])
                            else:
                                job_config_table.add_row(
                                    [
                                        job_Attribute,
                                        common.format_value(attribute_value),
                                    ]
                                )
                            # job_config.append([key,jobs[j][key]])
                            logger.debug(jobs[j][key])

                        # job_config_table.add_row(job_config)
                        # logger.trace(job_config_table)
                        job_name = j.upper()
                        logger.debug("### " + job_name)
                        # f = open(OUTPUT_FILE, "a")
                        if not job_name.startswith("."):
                            styled_job_name = f"""<h4><span class="badge text-bg-info">{job_name}</span></h4>"""
                        else:
                            styled_job_name = f"""<h4><span class="badge text-bg-secondary">{job_name}</span></h4>"""
                        add_between_markers(
                            file_path=OUTPUT_FILE, content=styled_job_name
                        )
                        add_between_markers(file_path=OUTPUT_FILE, content=str("\n"))
                        add_between_markers(file_path=OUTPUT_FILE, content="<hr>")
                        add_between_markers(file_path=OUTPUT_FILE, content=str("\n"))
                        # add_between_markers(file_path=OUTPUT_FILE, content=str("\n"))
                        add_between_markers(
                            file_path=OUTPUT_FILE, content=str(job_config_table)
                        )
                        # print(variable_table)

                        if rules_table is not None:
                            add_between_markers(
                                file_path=OUTPUT_FILE, content=str("\n")
                            )
                            add_between_markers(
                                file_path=OUTPUT_FILE, content=str(rules_table)
                            )

                        if value_counter > 0:
                            # print(variable_table)
                            add_between_markers(
                                file_path=OUTPUT_FILE, content=str("\n")
                            )
                            add_between_markers(
                                file_path=OUTPUT_FILE, content=str(variable_table)
                            )
                            add_between_markers(
                                file_path=OUTPUT_FILE, content=str("\n")
                            )
                        add_between_markers(file_path=OUTPUT_FILE, content=str("\n"))
                except AttributeError as e:
                    logger.info("Unable to pop job attribute")
                except Exception as e:
                    logger.info("Unable process job")
