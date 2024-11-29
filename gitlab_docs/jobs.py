import logging
import os
import yaml
from prettytable import MARKDOWN, PrettyTable
from prettytable.colortable import ColorTable, Themes
from prettytable import MARKDOWN as DESIGN
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GITLAB DOCS|JOBS WRAPPER")
logger.setLevel(LOG_LEVEL)


def env_var_replacement(loader, node):
    replacements = {
      '${VAR1}': '',
      '${VAR2}': '',
    }
    s = node.value
    # print("Debug !Reference Tag")
    # print(s)
    # for k, v in replacements.items():
    #     s = s.replace(k, v)
    # return s

# Define a loader class that will contain your custom logic
class EnvLoader(yaml.SafeLoader):
    pass


def get_jobs(OUTPUT_FILE, GLDOCS_CONFIG_FILE, WRITE_MODE, DISABLE_TITLE=True,DISABLE_TYPE_HEADING=True):
    exclude_keywords = ["default", "include", "stages", "variables", "workflow","image"]
    print("Generating Documentation for Jobs")
    
    with open(GLDOCS_CONFIG_FILE, "r") as file:
        EnvLoader.add_constructor('!reference', env_var_replacement)
        data = yaml.load(file, Loader=EnvLoader)
        jobs = data
        # Create file lock against output md file
        f = open(OUTPUT_FILE, "a")
        if not DISABLE_TITLE:
            f.write("\n")
            GLDOCS_CONFIG_FILE_HEADING = str("## " + GLDOCS_CONFIG_FILE + "\n")
            f.write("\n\n")
            f.write(GLDOCS_CONFIG_FILE_HEADING)
        if not DISABLE_TYPE_HEADING:
            f.write("\n")
            f.write(str("## " + "Jobs" + "\n"))
            f.write("\n")
            f.close()
        # print(type(jobs))
        for j in jobs:
            if j in exclude_keywords:
                logger.debug("Key is reserved for gitlab: " + j)
            else:
                # Build Row Level Table to store each job config in
                job_config_table_headers = ["**Key**", "**Value**"]

                job_config_table = PrettyTable(headers=job_config_table_headers)
                job_config_table.border = True
                job_config_table.set_style(DESIGN)
                # job_config_table.border=False
                jobs[j].pop("before_script", None)
                jobs[j].pop("script", None)
                jobs[j].pop("after_script", None)
                # print(jobs[j])
                job_config = []
                if jobs[j]:
                    for key in sorted(jobs[j]):
                        # job_config_table_headers.append(key)
                        job_property = '**' + key + '**'
                        value = str(jobs[j][key]).replace(",","\n").replace('{','').replace('}','')
                        print([job_property,value])


                        job_config_table.add_row([job_property,value])
                        # job_config.append([key,jobs[j][key]])
                        logger.debug(jobs[j][key])

                    job_config_table.field_names = job_config_table_headers
                    # job_config_table.add_row(job_config)
                    # print(job_config_table)
                    job_name = j.upper()
                    logger.debug("### " + job_name)
                    f = open(OUTPUT_FILE, "a")
                    f.write(str("\n"))
                    f.write(str("###" + job_name + "\n\n"))
                    f.write(str("\n"))
                    f.write(str(job_config_table))
                    f.write(str("\n"))
                    f.close()
        f = open(OUTPUT_FILE, "a")
        f.write(str("\n\n"))
        f.close()
