import os
import semver
import yaml
from prettytable import MARKDOWN, PrettyTable

import src.modules.common as common
import src.properties.jobs as jobs
from src.modules.logging import logger
from src.modules.doc_controller import add_between_markers


def document_includes(
    OUTPUT_FILE,
    GLDOCS_CONFIG_FILE,
    DISABLE_TITLE=False,
    DISABLE_TYPE_HEADING=True,
):
    logger.trace("Generating Documentation for Includes")

    if not os.path.exists(GLDOCS_CONFIG_FILE):
        logger.error(f"Config file not found: {GLDOCS_CONFIG_FILE}")
        return

    try:
        with open(GLDOCS_CONFIG_FILE, "r", encoding="utf-8") as file:
            try:
                data = yaml.load(file, Loader=common.EnvLoader)
            except yaml.YAMLError as e:
                logger.error(f"YAML error in {GLDOCS_CONFIG_FILE}: {e}")
                return

        includes = data.get("include")
        if not includes:
            logger.trace(f"No 'include' section found in {GLDOCS_CONFIG_FILE}")
            return

        includes_table = PrettyTable()
        includes_table.set_style(MARKDOWN)
        includes_table.field_names = [
            "Include Type", "Project", "Version", "Valid Version", "File", "Variables", "Rules"
        ]

        for i in includes:
            try:
                if isinstance(i, str):
                    logger.debug(f"Detected string include: {i}")
                    i = {"local": i}

                for key in i:
                    include_type = key
                    logger.debug(f"Include type: {include_type}")
                    value = i[key]

                    if include_type == "project":
                        version = i.get("ref", "")
                        file = i.get("file", "")
                        valid_version = (
                            "&#9989;" if check_include_version_is_sema_version(version, file, value)
                            else "&#x274c;"
                        )
                        inc_vars = i.get("variables", "")
                        inc_rules = i.get("rules", "")

                        includes_table.add_row([
                            include_type, value, version, valid_version, file, inc_vars, inc_rules
                        ])

                    elif include_type == "component":
                        try:
                            value, version = value.split("@")
                        except ValueError:
                            logger.error(f"Invalid component format: {value}")
                            continue

                        valid_version = (
                            "&#9989;" if check_include_version_is_sema_version(version, "component", value)
                            else "&#x274c;"
                        )
                        inc_vars = i.get("inputs", "")
                        inc_rules = i.get("rules", "")

                        includes_table.add_row([
                            include_type, value, version, valid_version, "", inc_vars, inc_rules
                        ])

                    elif include_type == "local":
                        version = "n/a"
                        inc_vars = i.get("variables", "")
                        inc_rules = i.get("rules", "")

                        includes_table.add_row([
                            include_type, value, version, "&#9989;", "", inc_vars, inc_rules
                        ])

                        # Recursively document nested includes
                        sub_config = value.lstrip("/")
                        try:
                            document_includes(
                                OUTPUT_FILE=OUTPUT_FILE,
                                GLDOCS_CONFIG_FILE=sub_config,
                                DISABLE_TITLE=True,
                                DISABLE_TYPE_HEADING=DISABLE_TYPE_HEADING,
                            )
                            jobs.get_jobs(
                                OUTPUT_FILE=OUTPUT_FILE,
                                GLDOCS_CONFIG_FILE=sub_config,
                                DISABLE_TITLE=True,
                                DISABLE_TYPE_HEADING=DISABLE_TYPE_HEADING,
                            )
                        except Exception as e:
                            logger.error(f"Error processing nested local include {value}: {e}")

                    else:
                        logger.warning(f"Unknown include type: {include_type}")
            except Exception as e:
                logger.error(f"Error processing include entry {i}: {e}")

        try:
            add_between_markers(file_path=OUTPUT_FILE, content="\n")
            add_between_markers(file_path=OUTPUT_FILE, content="## Includes\n\n")
            add_between_markers(file_path=OUTPUT_FILE, content=str(includes_table))
            add_between_markers(file_path=OUTPUT_FILE, content="\n")
        except Exception as e:
            logger.error(f"Failed to write documentation to {OUTPUT_FILE}: {e}")

        logger.debug("\n" + str(includes_table) + "\n")

    except Exception as e:
        logger.error(f"Unexpected error in document_includes: {e}")


def check_include_version_is_sema_version(version, file, include):
    try:
        is_valid = semver.Version.is_valid(version)
        if not is_valid:
            logger.warning(
                "Invalid SemVer: %s | File: %s | Include: %s",
                version, file, include
            )
        return is_valid
    except Exception as e:
        logger.error(f"Error validating SemVer '{version}': {e}")
        return False
