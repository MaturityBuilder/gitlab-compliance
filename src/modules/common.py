import html

import yaml

RULE_KEYS = [
    "if",
    "when",
    "changes",
    "exists",
    "variables",
    "allow_failure",
    "start_in",
    "needs",
    "interruptible",
]


def _ordered_dict_keys(items):
    keys = []
    for item in items:
        if isinstance(item, dict):
            for key in item:
                if key not in keys:
                    keys.append(key)
    preferred = [key for key in RULE_KEYS if key in keys]
    return preferred + [key for key in keys if key not in preferred]


def format_scalar(value):
    if value is None:
        return ""
    if isinstance(value, bool):
        return str(value)
    return str(value)


def format_string_list(items):
    if not items:
        return "[]"
    if all(isinstance(item, str) for item in items):
        return "\n".join(f"{index + 1}. {item}" for index, item in enumerate(items))
    return format_value(items)


def format_dict_summary(value):
    if not value:
        return ""
    if isinstance(value, dict):
        return "\n".join(f"{key}: {format_scalar(val)}" for key, val in value.items())
    return format_value(value)


def format_rules_summary(rules):
    if not rules:
        return ""
    if not isinstance(rules, list):
        return format_value(rules)

    lines = []
    for index, rule in enumerate(rules, 1):
        if isinstance(rule, dict):
            parts = [f"{key}={format_scalar(val)}" for key, val in rule.items()]
            lines.append(f"Rule {index}: " + ", ".join(parts))
        else:
            lines.append(f"Rule {index}: {format_scalar(rule)}")
    return "\n".join(lines)


def format_value(value):
    if isinstance(value, list):
        if all(isinstance(item, str) for item in value):
            return format_string_list(value)
        if all(isinstance(item, dict) for item in value):
            return format_rules_summary(value)
        return str(value)
    if isinstance(value, dict):
        return format_dict_summary(value)
    return format_scalar(value)


def dict_list_rows(items, row_label="Rule #"):
    if not items or not all(isinstance(item, dict) for item in items):
        return [], []

    ordered_keys = _ordered_dict_keys(items)
    headers = [row_label] + ordered_keys
    rows = []
    for index, item in enumerate(items, 1):
        row = [index]
        for key in ordered_keys:
            cell_value = item.get(key, "")
            row.append(format_value(cell_value) if cell_value != "" else "")
        rows.append(row)
    return headers, rows


def build_dict_list_table(items, row_label="Rule #"):
    headers, rows = dict_list_rows(items, row_label=row_label)
    if not headers:
        return None

    table = table_design(field_names=headers)
    for row in rows:
        table.add_row(row)
    return table


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


def format_description_cell(text) -> str:
    """Format YAML description scalars for markdown table cells."""
    if text is None:
        return "&#x274c;"
    if not isinstance(text, str):
        return str(text)
    stripped = text.strip()
    if not stripped:
        return "&#x274c;"
    if "\n" not in stripped:
        return stripped
    lines = [line.rstrip() for line in stripped.splitlines()]
    return "<br>".join(lines)


def format_structured_cell(value) -> str:
    """Format YAML scalars, lists, and objects for PrettyTable markdown cells."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return format_scalar(value)
    if isinstance(value, (int, float)):
        return format_scalar(value)
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        if not value:
            return "[]"
        if all(isinstance(item, str) for item in value):
            return "<br>".join(html.escape(item) for item in value)
        return "<br>".join(html.escape(format_scalar(item)) for item in value)
    if isinstance(value, dict):
        metadata_keys = {"description", "options", "expand"}
        display_items = [
            (key, val) for key, val in value.items() if key not in metadata_keys
        ]
        if not display_items:
            return ""
        if len(display_items) == 1:
            only_key, only_val = display_items[0]
            if only_key in ("default", "value"):
                return format_structured_cell(only_val)
        lines = []
        for key, val in display_items:
            inner = format_structured_cell(val)
            lines.append(f"<strong>{html.escape(str(key))}</strong>: {inner}")
        return "<br>".join(lines)
    return html.escape(str(value))


def format_options_cell(options) -> str:
    if options is None or options == "":
        return "&#x274c;"
    if isinstance(options, list):
        if not options:
            return "&#x274c;"
        return "<br>".join(html.escape(str(item)) for item in options)
    if isinstance(options, dict):
        return format_structured_cell(options)
    return html.escape(str(options))


def table_design(headers=[], field_names=[], style="MARKDOWN", column_align=None):

    from prettytable import PrettyTable, TableStyle
    from prettytable.colortable import ColorTable, Themes

    table = PrettyTable(headers=headers)
    if field_names:
        table.field_names = field_names
    else:
        table.field_names = headers
    table.border = True

    table.set_style(TableStyle.MARKDOWN)
    names = table.field_names
    if column_align:
        for name in names:
            table.align[name] = column_align.get(name, "c")
    else:
        table.align = "c"
        for header in names:
            table.align[header] = "c"
    return table
