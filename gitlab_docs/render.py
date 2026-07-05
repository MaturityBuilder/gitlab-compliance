"""Render documentation tables to multiple output formats."""

from __future__ import annotations

from dataclasses import dataclass, field

from gitlab_docs.constants import SUPPORTED_OUTPUT_FORMATS


@dataclass
class DocTable:
    headers: list[str]
    rows: list[list[str]] = field(default_factory=list)

    def add_row(self, row: list[str]) -> None:
        self.rows.append(row)


def render_table(table: DocTable, output_format: str = "markdown") -> str:
    fmt = output_format.lower()
    if fmt not in SUPPORTED_OUTPUT_FORMATS:
        raise ValueError(
            f"Unsupported format {output_format!r}; choose from "
            f"{', '.join(sorted(SUPPORTED_OUTPUT_FORMATS))}"
        )

    if not table.headers:
        return ""

    if fmt == "markdown":
        from prettytable import PrettyTable

        try:
            from prettytable import TableStyle

            table_style = TableStyle.MARKDOWN
        except ImportError:
            from prettytable import MARKDOWN

            table_style = MARKDOWN

        writer = PrettyTable()
        writer.set_style(table_style)
        writer.field_names = table.headers
        for row in table.rows:
            writer.add_row(row)
        return str(writer) + "\n"

    from pytablewriter import CsvTableWriter, HtmlTableWriter, JsonTableWriter

    writers = {
        "html": HtmlTableWriter,
        "json": JsonTableWriter,
        "csv": CsvTableWriter,
    }
    writer_cls = writers[fmt]
    writer = writer_cls()
    writer.headers = table.headers
    writer.value_matrix = table.rows
    return writer.dumps() + "\n"
