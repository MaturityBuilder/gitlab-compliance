import os
import yaml, json
from prettytable import MARKDOWN
from prettytable import MARKDOWN as DESIGN
from prettytable import PrettyTable
from prettytable.colortable import ColorTable, Themes
import src.modules.common as common
from src.modules.logging import logger
from src.modules.doc_controller import add_between_markers

def get_jobs(
    OUTPUT_FILE,
    GLDOCS_CONFIG_FILE,

    DISABLE_TITLE=True,
    DISABLE_TYPE_HEADING=True,
    detailed=False,
    experimental=False
):
    exclude_keywords = [
        "default",
        "include",
        "stages",
        "variables",
        "workflow",
        "image",
    ]
    logger.trace("Generating Documentation for Jobs")

    with open(GLDOCS_CONFIG_FILE, "r") as file:
        data = yaml.load(file, Loader=common.EnvLoader)
        jobs = data
        # Create file lock against output md file
        # f = open(OUTPUT_FILE, "a")
        if not DISABLE_TITLE:
            add_between_markers(file_path=OUTPUT_FILE, content="\n")
            GLDOCS_CONFIG_FILE_HEADING = str("## " + GLDOCS_CONFIG_FILE + "\n")
            add_between_markers(file_path=OUTPUT_FILE, content="\n")
            add_between_markers(file_path=OUTPUT_FILE, content=GLDOCS_CONFIG_FILE_HEADING)
        # if not DISABLE_TYPE_HEADING:
        #     add_between_markers(file_path=OUTPUT_FILE, content="\n")
        #     # add_between_markers(file_path=OUTPUT_FILE, content=str("## " + "Jobs" + "\n"))
        #     add_between_markers(file_path=OUTPUT_FILE, content="\n")

        # logger.trace(type(jobs))

        for j in jobs:
            if j in exclude_keywords:
                logger.debug("Key is reserved for gitlab: " + j)
            else:
                # Build Row Level Table to store each job config in
                job_config_table_headers = ["**Property**", "**Value**"]

                job_config_table = PrettyTable(headers=job_config_table_headers)
                job_config_table.border = True
                job_config_table.set_style(DESIGN)
                job_config_table.field_names = job_config_table_headers

                job_variables_config_table = PrettyTable()
                job_variables_config_table.border = True
                job_variables_config_table.set_style(DESIGN)
                job_variables_config_table.field_names = ['<span class="badge text-bg-danger">Type</span>','<span class="badge text-bg-warning">Key</span>','<span class="badge text-bg-success">Value</span>']
                # job_config_table.border=False
                if experimental is True:
                    if detailed is True and j["rules"]:
                        jobs[j].pop("rules", None)

                jobs[j].pop("before_script", None)
                jobs[j].pop("script", None)
                jobs[j].pop("after_script", None)
                # logger.trace(jobs[j])
                job_config = []

                value_counter = 0
                if jobs[j]:
                    for key in sorted(jobs[j]):
                        job_property = "**" + key + "**"
                        value = (
                            str(jobs[j][key])
                            .replace(",", "\n")
                            .replace("{", "")
                            .replace("}", "")
                        )
                        # job_config_table_headers.append(key)
                        if key in ["variables"]:
                            # print(json.dumps(jobs[j]["variables"].keys()))
                            # print(key)
                            var = jobs[j][key].keys()
                            # print(var)
                            # var=json.dumps(jobs[j][key])
                            # # .iteritems()
                            for item_key in var:
                                value = jobs[j][key][item_key]
                                value_counter = value_counter + 1
                                job_variables_config_table.add_row([key,item_key, value])
                        elif key in ["artifacts"] and type(key).__name__ != str:
                            var = jobs[j][key].keys()
                            for item_key in var:
                                value = jobs[j][key][item_key]
                                value_counter = value_counter + 1
                                job_variables_config_table.add_row([key,item_key, value])
                            # print(type(key).__name__)
                        elif key in ["needs"]:
                            # print("found extends")
                            # logger.warning(len(jobs[j][key]))
                            for x in jobs[j][key]:
                                value_counter = value_counter + 1
                                # print([key,"Hidden Job", x])
                                job_variables_config_table.add_row([key,"", x])
                        else:
                            job_config_table.add_row([job_property, value])
                        # job_config.append([key,jobs[j][key]])
                        logger.debug(jobs[j][key])

                    # job_config_table.add_row(job_config)
                    # logger.trace(job_config_table)
                    job_name = j.upper()
                    logger.debug("### " + job_name)
                    # f = open(OUTPUT_FILE, "a")
                    if not job_name.startswith('.'):
                        styled_job_name = f"""<h4><span class="badge text-bg-info">{job_name}</span></h4>"""
                    else:
                        styled_job_name = f"""<h4><span class="badge text-bg-secondary">{job_name}</span></h4>"""
                    add_between_markers(file_path=OUTPUT_FILE, content=styled_job_name)
                    add_between_markers(file_path=OUTPUT_FILE, content=str("\n"))
                    add_between_markers(file_path=OUTPUT_FILE, content="<hr>")
                    add_between_markers(file_path=OUTPUT_FILE, content=str("\n"))
                    # add_between_markers(file_path=OUTPUT_FILE, content=str("\n"))
                    add_between_markers(file_path=OUTPUT_FILE, content=str(job_config_table))
                    # print(job_variables_config_table)

                    if value_counter > 0:
                        # print(job_variables_config_table)
                        add_between_markers(file_path=OUTPUT_FILE, content=str("\n"))
                        add_between_markers(file_path=OUTPUT_FILE, content=str(job_variables_config_table))
                    add_between_markers(file_path=OUTPUT_FILE, content=str("\n"))
        # add_between_markers(file_path=OUTPUT_FILE, content=str("\n"))
