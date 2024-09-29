import logging
import os
import yaml
from prettytable import MARKDOWN, PrettyTable
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GITLAB DOCS|JOBS WRAPPER")
logger.setLevel(LOG_LEVEL)
OUTPUT_FILE = os.getenv("OUTPUT_FILE", "GITLAB-DOCS.md")

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


def get_jobs(GLDOCS_CONFIG_FILE, WRITE_MODE, DISABLE_TITLE=True,DISABLE_TYPE_HEADING=True):
    exclude_keywords = ["default", "include", "stages", "variables", "workflow","image"]
    print("Generating Documentation for Jobs")
    OUTPUT_FILE = os.getenv("OUTPUT_FILE", "GITLAB-DOCS.md")
    with open(GLDOCS_CONFIG_FILE, "r") as file:
        EnvLoader.add_constructor('!reference', env_var_replacement)
        data = yaml.load(file, Loader=EnvLoader)
        jobs = data
        # Create file lock against output md file
        f = open(OUTPUT_FILE, "a")
        if not DISABLE_TITLE:
            GLDOCS_CONFIG_FILE_HEADING = str("## " + GLDOCS_CONFIG_FILE + "\n\n")
            f.write("\n\n")
            f.write(GLDOCS_CONFIG_FILE_HEADING)
        if not DISABLE_TYPE_HEADING:
            f.write(str("## " + "Jobs" + "\n"))
            f.write("\n")
            f.close()
        # print(type(jobs))
        for j in jobs:
            if j in exclude_keywords:
                logger.debug("Key is reserved for gitlab: " + j)
            else:
                # Build Row Level Table to store each job config in
                job_config_table = PrettyTable()
                job_config_table.set_style(MARKDOWN)
                job_config_table_headers = []
                jobs[j].pop("before_script", None)
                jobs[j].pop("script", None)
                jobs[j].pop("after_script", None)
                job_config = []
                if jobs[j]:
                    for key in sorted(jobs[j]):
                        job_config_table_headers.append(key)
                        job_config.append(jobs[j][key])
                        logger.debug(jobs[j][key])

                    job_config_table.field_names = job_config_table_headers
                    job_config_table.add_row(job_config)
                    # print(job_config_table)
                    logger.debug("### " + j)
                    f = open(OUTPUT_FILE, "a")
                    f.write(str("### " + j + "\n"))
                    f.write(str(job_config_table))
                    f.write(str("\n"))
                    f.close()
