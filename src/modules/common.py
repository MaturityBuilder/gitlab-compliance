import yaml
from yaml.nodes import MappingNode, Node, ScalarNode, SequenceNode


def _reference_placeholder(loader: yaml.SafeLoader, node: Node) -> str:
    if isinstance(node, ScalarNode):
        return f"!reference {node.value}"
    if isinstance(node, SequenceNode):
        parts = loader.construct_sequence(node)
        return f"!reference {parts}"
    if isinstance(node, MappingNode):
        return f"!reference {loader.construct_mapping(node)}"
    return "!reference"


class EnvLoader(yaml.SafeLoader):
    pass


EnvLoader.add_constructor("!reference", _reference_placeholder)

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