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


def render_rules_markdown(items, row_label="Rule #"):
    """Render rules as a list when table rows would exceed 80 characters."""
    headers, rows = dict_list_rows(items, row_label=row_label)
    if not headers:
        return ""
    if any("\n" in str(cell) for row in rows for cell in row):
        pass
    else:
        table = render_markdown_table(headers, rows)
        if all(len(line) <= 80 for line in table.splitlines()):
            return table
    lines = []
    for row in rows:
        rule_id = row[0]
        lines.append(f"- **{row_label} {rule_id}**")
        for index, key in enumerate(headers[1:], start=1):
            value = row[index] if index < len(row) else ""
            if value != "":
                lines.append(f"  - **{key}:** `{value}`")
    return "\n".join(lines)


def build_dict_list_table(items, row_label="Rule #"):
    headers, rows = dict_list_rows(items, row_label=row_label)
    if not headers:
        return None
    return render_rules_markdown(items, row_label=row_label)


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


def table_design(headers=[], field_names=[], style="MARKDOWN"):

    from prettytable import PrettyTable, TableStyle
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


def render_markdown_table(headers, rows):
    """Render a markdownlint MD060-aligned pipe table."""
    if not headers:
        return ""
    str_headers = [str(h) for h in headers]
    str_rows = [[str(c) for c in row] for row in rows]
    widths = [len(h) for h in str_headers]
    for row in str_rows:
        for index, cell in enumerate(row):
            if index < len(widths):
                widths[index] = max(widths[index], len(cell))

    def format_row(cells):
        parts = []
        for index, width in enumerate(widths):
            cell = cells[index] if index < len(cells) else ""
            parts.append(f" {cell:<{width}} ")
        return "|" + "|".join(parts) + "|"

    separator = "|" + "|".join(f" {'-' * width} " for width in widths) + "|"
    lines = [format_row(str_headers), separator]
    lines.extend(format_row(row) for row in str_rows)
    return "\n".join(lines)


def render_table_or_list(headers, rows):
    """Render aligned table, falling back to a list if rows exceed 80 chars."""
    if not headers:
        return ""
    if any("\n" in str(cell) for row in rows for cell in row):
        pass
    else:
        table = render_markdown_table(headers, rows)
        if all(len(line) <= 80 for line in table.splitlines()):
            return table
    lines = []
    if len(headers) == 2:
        for row in rows:
            key = row[0] if row else ""
            value = row[1] if len(row) > 1 else ""
            if "\n" in str(value):
                lines.append(f"- **{key}:**")
                for part in str(value).splitlines():
                    lines.append(f"  {part}")
            else:
                line = f"- **{key}:** `{value}`"
                if len(line) <= 80:
                    lines.append(line)
                else:
                    lines.append(f"- **{key}:**")
                    lines.append(f"  `{value}`")
        return "\n".join(lines)
    for row in rows:
        lines.append(
            "- "
            + " · ".join(
                f"**{headers[i]}:** `{row[i]}`"
                for i in range(min(len(headers), len(row)))
            )
        )
    return "\n".join(lines)


def markdown_table_from_prettytable(table):
    """Convert a PrettyTable instance to markdown table or list."""
    headers = list(table.field_names)
    rows = [list(row) for row in table.rows]
    return render_table_or_list(headers, rows)
