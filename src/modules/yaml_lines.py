"""Map GitLab CI YAML structures to source line numbers."""

from __future__ import annotations

from yaml import MappingNode, SequenceNode, compose_all

from src.modules.common import EnvLoader

NON_JOB_KEYS = {"default", "include", "stages", "variables", "workflow", "image", "spec"}


def _line_number(node) -> int:
    return node.start_mark.line + 1


def index_yaml_file(config_file: str) -> dict:
    jobs: dict[str, int] = {}
    includes: list[int] = []
    variables: dict[str, int] = {}
    workflow_rules: list[int] = []

    with open(config_file, encoding="utf-8") as handle:
        for document in compose_all(handle, Loader=EnvLoader):
            if not isinstance(document, MappingNode):
                continue

            for key_node, value_node in document.value:
                key = key_node.value
                if key == "include" and isinstance(value_node, SequenceNode):
                    for item in value_node.value:
                        includes.append(_line_number(item))
                    continue

                if key == "variables" and isinstance(value_node, MappingNode):
                    for variable_key, _variable_value in value_node.value:
                        variables[variable_key.value] = _line_number(variable_key)
                    continue

                if key == "workflow":
                    if isinstance(value_node, MappingNode):
                        for workflow_key, workflow_value in value_node.value:
                            if workflow_key.value == "rules" and isinstance(workflow_value, SequenceNode):
                                for item in workflow_value.value:
                                    workflow_rules.append(_line_number(item))
                    elif isinstance(value_node, SequenceNode):
                        for item in value_node.value:
                            workflow_rules.append(_line_number(item))
                    continue

                if key in NON_JOB_KEYS and not key.startswith("."):
                    continue
                if isinstance(value_node, MappingNode):
                    jobs[key] = _line_number(key_node)

    return {
        "jobs": jobs,
        "includes": includes,
        "variables": variables,
        "workflow_rules": workflow_rules,
    }
