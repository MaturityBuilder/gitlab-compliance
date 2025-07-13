import os
import semver
import yaml
from prettytable import MARKDOWN, PrettyTable
import src.modules.common as common
import src.properties.jobs as jobs
from src.modules.logging import logger
from src.modules.reset_docs import add_between_markers

def document_includes(
    OUTPUT_FILE,
    GLDOCS_CONFIG_FILE,

    DISABLE_TITLE=False,
    DISABLE_TYPE_HEADING=True,
):
    logger.trace("Generating Documentation for Includes")
    with open(GLDOCS_CONFIG_FILE, "r") as file:
        try:
            data = yaml.load(file, Loader=common.EnvLoader)
            if "include" in data:
                includes = data["include"]

                # logger.trace(gldocs.generate_markdown_table(includes))

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
                logger.log("DEBUG",includes)

                for i in includes:

                    if isinstance(i, (str)):
                        logger.log("DEBUG",i)
                        i = {"local": i}
                    logger.log("DEBUG",i)
                    for key in i.keys():
                        type = key
                        logger.log("DEBUG","Type is: " + key)
                        if type == "project":
                            logger.log("DEBUG","Type is: " + key)
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
                                logger.log("DEBUG","No rules found for: %s", value)
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
                                logger.log("DEBUG","No rules found for: %s", value)
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
                                logger.log("DEBUG","No Variables found for: %s", value)

                            inc_rules = ""
                            try:
                                inc_rules = i["rules"]
                            except KeyError:
                                logger.log("DEBUG","No rules found for: %s", value)
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
                                    if str(SUB_GLDOCS_CONFIG_FILE)[0] == "/":
                                        SUB_GLDOCS_CONFIG_FILE = SUB_GLDOCS_CONFIG_FILE[
                                            1:
                                        ]
                                    document_includes(
                                        OUTPUT_FILE=OUTPUT_FILE,
                                        GLDOCS_CONFIG_FILE=SUB_GLDOCS_CONFIG_FILE,

                                    )

                                    jobs.get_jobs(
                                        OUTPUT_FILE=OUTPUT_FILE,
                                        GLDOCS_CONFIG_FILE=SUB_GLDOCS_CONFIG_FILE,

                                        DISABLE_TITLE=True,
                                        DISABLE_TYPE_HEADING=DISABLE_TYPE_HEADING,
                                    )
                                except KeyError:
                                    logger.log("DEBUG",
                                        "include don't exist in " + GLDOCS_CONFIG_FILE
                                    )

                # f = open(OUTPUT_FILE, "a")
                # GLDOCS_CONFIG_FILE_HEADING = str("## " + GLDOCS_CONFIG_FILE + "\n\n")
                # add_between_markers(GLDOCS_CONFIG_FILE_HEADING)

                add_between_markers("\n")
                add_between_markers(str("## " + "Includes" + "\n\n"))
                add_between_markers(str(includes_table))
                add_between_markers("\n")
                # f.close()
                logger.log("DEBUG","")
                logger.log("DEBUG",str(includes_table))
                logger.log("DEBUG","")
        except yaml.YAMLError as exc:
            logger.trace(exc)


def check_include_version_is_sema_version(version, file, include):

    logger.log("DEBUG","Is Version Sem Ver:" + str(semver.Version.is_valid(version)))
    if not semver.Version.is_valid(version):
        logger.warning(
            "Is Version Sem Ver: %s | File: %s | Include: %s",
            str(semver.Version.is_valid(version)),
            file,
            include,
        )
    return semver.Version.is_valid(version)
