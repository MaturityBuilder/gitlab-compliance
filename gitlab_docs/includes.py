import logging
import os

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GITLAB DOCS|INCLUDES WRAPPER")
logger.setLevel(LOG_LEVEL)
OUTPUT_FILE = os.getenv("OUTPUT_FILE", "GITLAB-DOCS.md")


def document_includes(GLDOCS_CONFIG_FILE, WRITE_MODE="a"):
    print("Generating Documentation for Includes")
    OUTPUT_FILE = os.getenv("OUTPUT_FILE", "GITLAB-DOCS.md")
    import yaml
    from prettytable import MARKDOWN

    with open(GLDOCS_CONFIG_FILE, "r") as file:
        try:
            data = yaml.load(file, Loader=yaml.SafeLoader)
            if "include" in data:
                includes = data["include"]

                # print(gldocs.generate_markdown_table(includes))
                from prettytable import PrettyTable

                includes_table = PrettyTable()
                includes_table.set_style(MARKDOWN)
                includes_table.field_names = [
                    "Include Type",
                    "Project",
                    "Version",
                    "Valid Version",
                    "File",
                    "Variables",
                    "Rules",
                ]
                # includes_table.add_rows([includes])
                logger.debug(includes)

                for i in includes:

                    if isinstance(i, (str)):
                        logger.debug(i)
                        i = {"local": i}
                    logger.debug(i)
                    for key in i.keys():
                        type = key
                        logger.debug("Type is: " + key)
                        if type == "project":
                            logger.debug("Type is: " + key)
                            version = i["ref"]
                            value = i["project"]
                            file = i["file"]
                            if check_include_version_is_sema_version(
                                version, file=file, include=value
                            ):
                                valid_version = "&#9989;"
                            else:
                                valid_version = "&#x274c;"
                            inc_vars = ""
                            try:
                                inc_vars = i["variables"]
                            except KeyError:
                                logger.warning("No Inputs found for: %s", value)
                            inc_rules = ""
                            try:
                                inc_rules = i["rules"]
                            except KeyError:
                                logger.debug("No rules found for: %s", value)
                            includes_table.add_row(
                                [
                                    type,
                                    value,
                                    version,
                                    valid_version,
                                    file,
                                    inc_vars,
                                    inc_rules,
                                ]
                            )

                        elif type == "component":

                            version = i["component"].split("@")[1]
                            value = i["component"].split("@")[0]
                            if check_include_version_is_sema_version(
                                version, file="component", include=value
                            ):
                                valid_version = "&#9989;"
                            else:
                                valid_version = "&#x274c;"

                            inc_vars = ""
                            try:
                                inc_vars = i["inputs"]
                            except KeyError:
                                logger.warning("No Inputs found for: %s", value)

                            inc_rules = ""
                            try:
                                inc_rules = i["rules"]
                            except KeyError:
                                logger.debug("No rules found for: %s", value)
                            includes_table.add_row(
                                [
                                    type,
                                    value,
                                    version,
                                    valid_version,
                                    "",
                                    inc_vars,
                                    inc_rules,
                                ]
                            )
                        elif type == "local":
                            version = "n/a"
                            value = i[key]
                            inc_vars = ""
                            try:
                                inc_vars = i["variables"]
                            except KeyError:
                                logger.debug("No Variables found for: %s", value)

                            inc_rules = ""
                            try:
                                inc_rules = i["rules"]
                            except KeyError:
                                logger.debug("No rules found for: %s", value)
                            includes_table.add_row(
                                [
                                    type,
                                    value,
                                    version,
                                    "&#9989;",
                                    "",
                                    inc_vars,
                                    inc_rules,
                                ]
                            )
                            if type == "local":
                                SUB_GLDOCS_CONFIG_FILE = "" + i[key]
                                try:
                                    document_includes(
                                        GLDOCS_CONFIG_FILE=SUB_GLDOCS_CONFIG_FILE,
                                        WRITE_MODE="a",
                                    )
                                    import jobs as jobs

                                    jobs.get_jobs(
                                        GLDOCS_CONFIG_FILE=SUB_GLDOCS_CONFIG_FILE,
                                        WRITE_MODE="a",
                                    )
                                except KeyError:
                                    logger.debug(
                                        "include don't exist in " + GLDOCS_CONFIG_FILE
                                    )

                GLDOCS_CONFIG_FILE_HEADING = str("## " + GLDOCS_CONFIG_FILE + "\n\n")
                f = open(OUTPUT_FILE, "a")
                f.write("\n\n")
                f.write(GLDOCS_CONFIG_FILE_HEADING)
                f.write(str(includes_table))
                f.close()
                logger.debug("")
                logger.debug(str(includes_table))
                logger.debug("")
        except yaml.YAMLError as exc:
            print(exc)


def check_include_version_is_sema_version(version, file, include):
    import semver

    logger.debug("Is Version Sem Ver:" + str(semver.Version.is_valid(version)))
    if not semver.Version.is_valid(version):
        logger.warning(
            "Is Version Sem Ver: %s | File: %s | Include: %s",
            str(semver.Version.is_valid(version)),
            file,
            include,
        )
    return semver.Version.is_valid(version)
