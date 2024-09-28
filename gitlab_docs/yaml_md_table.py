# import sys
# from pathlib import Path
# import oyaml as yaml
from prettytable import PrettyTable


def generate_markdown_table(data):
    table = PrettyTable()
    table.field_names = ["Include Type", "Project/File", "Version"]
