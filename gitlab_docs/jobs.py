import logging, os
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GITLAB DOCS|JOBS WRAPPER")
logger.setLevel(LOG_LEVEL)
OUTPUT_FILE=os.getenv("OUTPUT_FILE", "README.md")
def get_jobs(GLDOCS_CONFIG_FILE,WRITE_MODE):
    exclude_keywords = ["default", "include", "stages","variables", "workflow"]
    print("Generating Documentation for Jobs")
    OUTPUT_FILE=os.getenv("OUTPUT_FILE", "README.md")
    import yaml
    from pytablewriter import MarkdownTableWriter
    from prettytable import MARKDOWN
    from prettytable import PrettyTable

    jobs_table = PrettyTable()
    jobs_table.set_style(MARKDOWN)
    jobs_table.field_names = ["Job Name", "Config"]
    with open(GLDOCS_CONFIG_FILE, 'r') as file:
        # try:
            data = yaml.load(file, Loader=yaml.SafeLoader)
            jobs = data
            cleaned_jobs = data
            print(jobs)
            for j in jobs.keys():
                if j in exclude_keywords:
                    logger.debug("Key is reserved for gitlab: " + j)
                else:
                    print("Found Job:" + j)
                    print(jobs[j])
                    config=jobs[j]
                    job_name=j
                    jobs_table.add_row([job_name, config])

    logger.debug("")
    logger.debug(str(jobs_table))
    logger.debug("")

    GLDOCS_CONFIG_FILE_HEADING = str("## " + GLDOCS_CONFIG_FILE + "\n\n")
    f = open(OUTPUT_FILE, "a")
    f.write("\n\n")
    f.write(GLDOCS_CONFIG_FILE_HEADING)
    f.write(str(jobs_table))
    f.close()

        # except error:
            # logger.debug("An Error Occured whilst documenting the jobs")
