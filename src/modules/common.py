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
