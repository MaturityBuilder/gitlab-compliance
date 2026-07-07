# import sys
# from pathlib import Path
# import oyaml as yaml
from prettytable import PrettyTable


def generate_markdown_table(data):
    table = PrettyTable()
    table.field_names = ["Include Type", "Project/File", "Version"]
    for item in data or []:
        if isinstance(item, str):
            table.add_row(["local", item, "n/a"])
        elif isinstance(item, dict):
            if "local" in item:
                table.add_row(["local", item["local"], "n/a"])
            elif "project" in item:
                table.add_row(["project", item.get("project", ""), item.get("ref", "")])
            elif "component" in item:
                component = item["component"]
                if "@" in component:
                    project, version = component.rsplit("@", 1)
                    table.add_row(["component", project, version])
                else:
                    table.add_row(["component", component, ""])
            else:
                keys = list(item.keys())
                first_key = keys[0] if keys else ""
                table.add_row([first_key, str(item.get(first_key, "")), ""])
    return table.get_string()
