import yaml
from yaml.nodes import ScalarNode


def env_var_replacement(loader: yaml.SafeLoader, node: ScalarNode) -> str:
    """Placeholder for GitLab !reference tags so YAML parsing can continue."""
    return f"!reference {node.value}"


class EnvLoader(yaml.SafeLoader):
    pass


EnvLoader.add_constructor("!reference", env_var_replacement)
