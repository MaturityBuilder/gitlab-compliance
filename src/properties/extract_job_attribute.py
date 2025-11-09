import os
import yaml, json
import src.modules.common as common
from src.modules.logging import logger
from src.modules.doc_controller import add_between_markers, add_between_markers

def get_job_attribute(
    OUTPUT_FILE,
    GLDOCS_CONFIG_FILE,
    DISABLE_TITLE=True,
    DISABLE_TYPE_HEADING=True,
    detailed=False,
    experimental=False,
    attributes="image",
    json_format=False,
):
    exclude_keywords = [
        "include",
        "stages",
        "variables",
        "workflow",
        "spec",
    ]
    
    # Setup table
    attribute_tb_headers = ["**File**", "Job Name"]        
    attributes = attributes.split(',')
    for a in attributes:
        attribute_tb_headers.append(a)
        if a in exclude_keywords:
            exclude_keywords.pop(a)

    attribute_table = common.table_design(field_names=attribute_tb_headers)
    file = common.read_yml(GLDOCS_CONFIG_FILE)
    marker_start="[comment]: <> (gitlab-docs-attribute-opening-auto-generated)"
    marker_end="[comment]: <> (gitlab-docs-attribute-closing-auto-generated)"
    add_between_markers(file_path=OUTPUT_FILE, content="\n",marker_start=marker_start,marker_end=marker_end)
    for jobs in file:
        for j in jobs:
            notfound_counter=0
            if j not in exclude_keywords:
                job_result = [GLDOCS_CONFIG_FILE,j]
                for a in attributes:
                    
                    if a in jobs[j]:
                        
                        job_result.append(jobs[j][a])
                        
                    else:
                        job_result.append("Not Found")
                        notfound_counter=notfound_counter+1
                if len(attributes) != notfound_counter:
                    attribute_table.add_row(job_result)
    attribute_table.get_html_string()
    add_between_markers(file_path=OUTPUT_FILE, content=str(attribute_table),marker_start=marker_start,marker_end=marker_end)
    if json_format:
        print(attribute_table.get_json_string())