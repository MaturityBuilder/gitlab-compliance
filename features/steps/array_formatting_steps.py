import json

from behave import given, then, when

from src.modules.common import (
    build_dict_list_table,
    format_rules_summary,
    format_string_list,
)


@given("rules data:")
def step_rules_data(context):
    context.rules_data = json.loads(context.text)


@given('a string list "{_label}" with values "{values}"')
def step_string_list(context, _label, values):
    context.string_list = [value.strip() for value in values.split(",")]


@when("I build a rules table from the data")
def step_build_rules_table(context):
    context.rules_table = build_dict_list_table(context.rules_data)


@when("I format the string list for a table cell")
def step_format_string_list(context):
    context.formatted_value = format_string_list(context.string_list)


@when("I format the rules summary")
def step_format_rules_summary(context):
    context.formatted_value = format_rules_summary(context.rules_data)


@then('the rules table should contain column "{column_name}"')
def step_rules_table_has_column(context, column_name):
    assert column_name in context.rules_table.field_names


@then('the rules table should contain row value "{expected_value}"')
def step_rules_table_has_row_value(context, expected_value):
    table_output = str(context.rules_table)
    assert expected_value in table_output


@then("the formatted value should be:")
def step_formatted_value_is(context):
    expected = context.text.strip()
    assert context.formatted_value == expected


@then('the formatted value should contain "{expected_text}"')
def step_formatted_value_contains(context, expected_text):
    assert expected_text in context.formatted_value
