import yaml
def env_var_replacement(loader, node):
    replacements = {
        "${VAR1}": "",
        "${VAR2}": "",
    }
    s = node.value
class EnvLoader(yaml.SafeLoader):
    pass

EnvLoader.add_constructor("!reference", env_var_replacement)

def read_yml(GLDOCS_CONFIG_FILE):
    with open(GLDOCS_CONFIG_FILE, "r") as f:
        documents = list(yaml.load_all(f, Loader=EnvLoader))
    return documents

def table_design(headers=[],field_names=[],style="MARKDOWN"):
    
    from prettytable import TableStyle
    from prettytable import PrettyTable
    from prettytable.colortable import ColorTable, Themes
    table = PrettyTable(headers=headers)
    if field_names:
        table.field_names = field_names
    else:
        table.field_names = headers
    table.border = True
    
    table.set_style(TableStyle.MARKDOWN)
    # table.sortby = headers[0]
    table.align = "c"
    for header in headers:
        table.align[header] = "c"
    return table