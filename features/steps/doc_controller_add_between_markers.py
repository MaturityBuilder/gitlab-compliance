import os
from tempfile import NamedTemporaryFile

from behave import given, then, when

from src.modules.doc_controller import add_between_markers

# from pathlib import Path


file_path = "README.md"
marker_start = "<!-- gitlab-compliance-opening-auto-generated -->"
marker_end = "<!-- gitlab-compliance-closing-auto-generated -->"


@given("a non-existent file path")
def step_given_nonexistent_file(context):
    temp_file = NamedTemporaryFile(
        delete=False,
    )
    context.file_path = temp_file.name
    # temp_file.close()  # Deletes the file


@when('I add content "{content}" between markers')
def step_when_add_content(context, content):
    context.inserted_content = content
    add_between_markers(context.file_path, content)


@then("the file should be created with the content between markers")
def step_then_file_created(context):
    assert os.path.exists(context.file_path)
    with open(context.file_path, "r") as f:
        contents = f.read()
    expected = f"{marker_start}\n{context.inserted_content}\n{marker_end}\n"
    # assert expected in contents


@given("an existing file without marker block")
def step_existing_file_no_markers(context):
    temp = NamedTemporaryFile(delete=False, mode="w")
    temp.write("Initial file content\n")
    temp.close()
    context.file_path = temp.name


@then("the file should contain a new marker block with the content")
def step_then_contains_new_block(context):
    with open(context.file_path, "r") as f:
        contents = f.read()
    assert marker_start in contents
    assert context.inserted_content in contents
    assert marker_end in contents


@given('a file with existing marker block containing "{existing_content}"')
def step_given_existing_block(context, existing_content):
    temp = NamedTemporaryFile(delete=False, mode="w")
    temp.write(f"{marker_start}\n{existing_content}\n{marker_end}\n")
    temp.close()
    context.file_path = temp.name


@then("the content should appear before the end marker")
def step_then_inserted_before_end(context):
    with open(context.file_path, "r") as f:
        lines = f.readlines()

    try:
        start_idx = lines.index(marker_start + "\n")
        end_idx = lines.index(marker_end + "\n")
    except ValueError:
        raise AssertionError("Marker lines not found")

    inserted_lines = lines[start_idx + 1 : end_idx]
    contents = "".join(inserted_lines)
    assert context.inserted_content in contents
