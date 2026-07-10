from types import SimpleNamespace

import pytest

from src.modules.common import (
    EnvLoader,
    build_dict_list_table,
    dict_list_rows,
    env_var_replacement,
    format_dict_summary,
    format_rules_summary,
    format_scalar,
    format_string_list,
    format_value,
    read_yml,
    table_design,
)


class TestFormatHelpers:
    def test_format_scalar(self):
        assert format_scalar(None) == ""
        assert format_scalar(True) == "True"
        assert format_scalar("x") == "x"

    def test_format_string_list(self):
        assert format_string_list([]) == "[]"
        assert "1. a" in format_string_list(["a", "b"])
        assert format_string_list([{"k": "v"}])  # mixed path via format_value

    def test_format_rules_summary(self):
        assert format_rules_summary([]) == ""
        assert "Rule 1" in format_rules_summary([{"if": "$CI"}])
        assert format_rules_summary("single")  # non-list

    def test_format_value_branches(self):
        assert format_value(["a", "b"]) == "1. a\n2. b"
        assert "Rule 1" in format_value([{"when": "always"}])
        assert format_value([1, 2]) == "[1, 2]"
        assert "k: v" in format_value({"k": "v"})

    def test_dict_list_rows_invalid(self):
        assert dict_list_rows([]) == ([], [])
        assert dict_list_rows(["not-a-dict"]) == ([], [])

    def test_build_dict_list_table(self):
        table = build_dict_list_table([{"if": "main", "when": "always"}])
        assert table is not None
        assert "if" in table
        assert "when" in table


class TestReadYml:
    def test_read_yml_multi_document(self, tmp_path):
        path = tmp_path / "multi.yml"
        path.write_text(
            "---\nname: one\nage: 1\n---\nname: two\nage: 2\n", encoding="utf-8"
        )
        docs = read_yml(str(path))
        assert len(docs) == 2
        assert docs[0]["name"] == "one"


class TestEnvLoader:
    def test_reference_constructor(self):
        node = SimpleNamespace(value="${VAR1}")
        env_var_replacement(None, node)


class TestTableDesign:
    def test_table_design_with_field_names(self):
        table = table_design(headers=["A", "B"], field_names=["ColA", "ColB"])
        assert table.field_names == ["ColA", "ColB"]


class TestRenderTableOrList:
    def test_renders_pipe_table_for_wide_rows(self):
        from src.modules.common import render_table_or_list

        rows = [["extends", "1. .build:python\n2. .test:rules"]]
        text = render_table_or_list(["Attribute", "Value"], rows)
        assert text.startswith("|")
        assert "- **" not in text
        assert "<br>" in text
