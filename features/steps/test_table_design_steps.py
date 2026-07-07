from behave import given, then
from prettytable import TableStyle

from src.modules.common import table_design


@given('a table is created with headers "{headers}" and field names "{field_names}"')
def step_create_table_with_field_names(context, headers, field_names):
    headers_list = [h.strip() for h in headers.split(",")]
    field_names_list = [f.strip() for f in field_names.split(",")]
    context.pretty_table = table_design(
        headers=headers_list, field_names=field_names_list
    )


@given('a table is created with headers "{headers}" and no field names')
def step_create_table_no_field_names(context, headers):
    headers_list = [h.strip() for h in headers.split(",")]
    context.pretty_table = table_design(headers=headers_list)


@then('the table should have field names "{expected}"')
def step_check_field_names(context, expected):
    expected_list = [e.strip() for e in expected.split(",")]
    assert (
        context.pretty_table.field_names == expected_list
    ), f"Expected field names {expected_list}, but got {context.pretty_table.field_names}"


@then("the table should have borders enabled")
def step_check_borders(context):
    assert context.pretty_table.border is True, "Table borders are not enabled"


@then("all columns should be center-aligned")
def step_check_alignment(context):
    for col in context.pretty_table.field_names:
        assert (
            context.pretty_table.align[col] == "c"
        ), f"Column '{col}' is not center-aligned"


@then('the table style should be "MARKDOWN"')
def step_check_style(context):
    assert context.pretty_table._style == 13, "Table style is not MARKDOWN"
