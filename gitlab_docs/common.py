import yaml
from yaml.nodes import MappingNode, Node, ScalarNode, SequenceNode


def _reference_placeholder(loader: yaml.SafeLoader, node: Node) -> str:
    """Placeholder for GitLab !reference tags so YAML parsing can continue."""
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
