import os
import tempfile

from behave import given, then, when

from src.modules.common import EnvLoader  # make sure EnvLoader is imported
from src.modules.common import read_yml  # adjust import to your module


@given('a YAML file "{filename}" with content')
def step_create_yaml_file(context, filename):
    context.temp_file = tempfile.NamedTemporaryFile(
        mode="w+", delete=False, suffix=".yml"
    )
    context.temp_file.write(context.text)
    context.temp_file.flush()
    context.temp_file.close()
    context.yaml_file_path = context.temp_file.name


@when("I read the YAML file using read_yml")
def step_read_yaml(context):
    context.documents = read_yml(context.yaml_file_path)


@then("I should get {count:d} documents")
def step_check_document_count(context, count):
    assert (
        len(context.documents) == count
    ), f"Expected {count} documents, got {len(context.documents)}"


@then('the first document should have name "{name}" and age {age:d}')
def step_check_first_document(context, name, age):
    doc = context.documents[0]
    assert doc["name"] == name
    assert doc["age"] == age


@then('the second document should have name "{name}" and age {age:d}')
def step_check_second_document(context, name, age):
    doc = context.documents[1]
    assert doc["name"] == name
    assert doc["age"] == age


# Optional: cleanup temporary file
def after_scenario(context, scenario):
    if hasattr(context, "yaml_file_path") and os.path.exists(context.yaml_file_path):
        os.remove(context.yaml_file_path)
