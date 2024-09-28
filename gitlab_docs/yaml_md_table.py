import sys
from pathlib import Path
import oyaml as yaml
from prettytable import PrettyTable
import argparse

def generate_markdown_table(data):
    from prettytable import PrettyTable
    table = PrettyTable()
    table.field_names = ["Include Type", "Project/File", "Version"]
