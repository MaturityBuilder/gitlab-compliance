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


def _render_single_job(OUTPUT_FILE, job: dict, detailed: bool = False):
    """Write one job block to *OUTPUT_FILE* from structured pipeline data."""
    job_config_table = common.table_design(headers=["**Attribute**", "**Value**"])
    variable_table = common.table_design(
        headers=["**Attribute**", "**Key**", "**Value**"]
    )
    rules_table = None
    value_counter = 0

    for item in job.get("attributes", []):
        key = item["key"]
        attribute_value = item["value"]
        if key == "rules" and isinstance(attribute_value, list):
            rules_table = common.build_dict_list_table(attribute_value)
        else:
            job_config_table.add_row(
                [f"**{key}**", common.format_value(attribute_value)]
            )

    if detailed and job.get("rules"):
        rules_table = common.build_dict_list_table(job["rules"])

    for item in job.get("nested", []):
        value_counter += 1
        variable_table.add_row([item["attribute"], item.get("key", ""), item["value"]])

    job_name = job.get("display_name", job.get("name", "").upper())
    kind = "TEMPLATE" if job.get("is_template") else "JOB"
    styled_job_name = f"### {kind} · {job_name}"
    add_between_markers(file_path=OUTPUT_FILE, content="\n")
    add_between_markers(file_path=OUTPUT_FILE, content=styled_job_name)
    add_between_markers(file_path=OUTPUT_FILE, content="\n")
    add_between_markers(
        file_path=OUTPUT_FILE,
        content=common.markdown_table_from_prettytable(job_config_table),
    )

    if rules_table is not None:
        add_between_markers(file_path=OUTPUT_FILE, content=str("\n"))
        add_between_markers(file_path=OUTPUT_FILE, content=rules_table)

    if value_counter > 0:
        add_between_markers(file_path=OUTPUT_FILE, content=str("\n"))
        add_between_markers(
            file_path=OUTPUT_FILE,
            content=common.markdown_table_from_prettytable(variable_table),
        )
        add_between_markers(file_path=OUTPUT_FILE, content=str("\n"))
    add_between_markers(file_path=OUTPUT_FILE, content=str("\n"))


def render_jobs_from_pipeline(OUTPUT_FILE, pipeline_data: dict, detailed=False):
    """Render jobs from filtered/grouped pipeline data."""
    logger.trace("Generating Documentation for Jobs from pipeline data")
    add_between_markers(file_path=OUTPUT_FILE, content="\n\n## Jobs\n")

    group_by = pipeline_data.get("group_by")
    for block in pipeline_data.get("jobs_grouped", []):
        group_key = block.get("group_key", "")
        if group_by and group_key:
            heading = f"### {group_by.title()} · {group_key}"
            add_between_markers(file_path=OUTPUT_FILE, content="\n")
            add_between_markers(file_path=OUTPUT_FILE, content=heading)
            add_between_markers(file_path=OUTPUT_FILE, content="\n")

        for job in block.get("jobs", []):
            _render_single_job(OUTPUT_FILE, job, detailed=detailed)


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
    add_between_markers(file_path=OUTPUT_FILE, content="\n\n## Jobs\n")
    for jobs in file:
        for j in jobs:
            if j in exclude_keywords and not j.startswith("."):
                logger.debug("Key is reserved for gitlab: " + j)
            else:
                job_config_table = common.table_design(
                    headers=["**Attribute**", "**Value**"]
                )
                variable_table = common.table_design(
                    headers=["**Attribute**", "**Key**", "**Value**"]
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
                    job_config = []
                    value_counter = 0
                    if jobs[j]:
                        for key in sorted(jobs[j]):
                            job_Attribute = "**" + key + "**"
                            attribute_value = jobs[j][key]
                            if key == "rules" and isinstance(attribute_value, list):
                                rules_table = common.build_dict_list_table(
                                    attribute_value
                                )
                            elif key in ["variables"]:
                                var = attribute_value.keys()
                                for item_key in var:
                                    value = attribute_value[item_key]
                                    value_counter = value_counter + 1
                                    variable_table.add_row([key, item_key, value])
                            elif key == "artifacts" and isinstance(
                                attribute_value, dict
                            ):
                                var = attribute_value.keys()
                                for item_key in var:
                                    value = attribute_value[item_key]
                                    value_counter = value_counter + 1
                                    variable_table.add_row([key, item_key, value])
                            elif key in ["needs"]:
                                for x in attribute_value:
                                    value_counter = value_counter + 1
                                    variable_table.add_row([key, "", x])
                            else:
                                job_config_table.add_row(
                                    [
                                        job_Attribute,
                                        common.format_value(attribute_value),
                                    ]
                                )
                            logger.debug(jobs[j][key])

                        job_name = j.upper()
                        logger.debug("### " + job_name)
                        kind = "TEMPLATE" if job_name.startswith(".") else "JOB"
                        styled_job_name = f"### {kind} · {job_name}"
                        add_between_markers(file_path=OUTPUT_FILE, content="\n")
                        add_between_markers(
                            file_path=OUTPUT_FILE, content=styled_job_name
                        )
                        add_between_markers(file_path=OUTPUT_FILE, content="\n")
                        add_between_markers(
                            file_path=OUTPUT_FILE,
                            content=common.markdown_table_from_prettytable(
                                job_config_table
                            ),
                        )

                        if rules_table is not None:
                            add_between_markers(
                                file_path=OUTPUT_FILE, content=str("\n")
                            )
                            add_between_markers(
                                file_path=OUTPUT_FILE, content=rules_table
                            )

                        if value_counter > 0:
                            add_between_markers(
                                file_path=OUTPUT_FILE, content=str("\n")
                            )
                            add_between_markers(
                                file_path=OUTPUT_FILE,
                                content=common.markdown_table_from_prettytable(
                                    variable_table
                                ),
                            )
                            add_between_markers(
                                file_path=OUTPUT_FILE, content=str("\n")
                            )
                        add_between_markers(file_path=OUTPUT_FILE, content=str("\n"))
                except AttributeError as e:
                    logger.info("Unable to pop job attribute")
                except Exception as e:
                    logger.info("Unable process job")
