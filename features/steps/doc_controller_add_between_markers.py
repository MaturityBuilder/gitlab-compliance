import os
from behave import given, when, then
from src.modules.doc_controller import add_between_markers, marker_start, marker_end, file_path

# @given('the file "README.md" does not exist')
# def step_file_does_not_exist(context):
#     if os.path.exists(file_path):
#         os.remove(file_path)

@given('the file "README.md" contains block')
def step_file_contains_existing_block(context):
    content = context.text.strip()
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"{marker_start}\n{content}\n{marker_end}\n")

@when('I add between markers')
def step_add_between_markers(context):
    add_between_markers(context.text)

@then('the file "README.md" should contain')
def step_file_should_contain(context):
    expected_lines = context.text.strip().splitlines()
    with open(file_path, "r", encoding="utf-8") as f:
        contents = f.read()

    # Extract everything between the markers
    start_idx = contents.find(marker_start)
    end_idx = contents.find(marker_end)
    assert start_idx != -1 and end_idx != -1, "Markers not found in file"

    between = contents[start_idx:end_idx].splitlines()[1:]  # exclude start marker
    actual_content = [line.strip() for line in between]
    expected_content = [line.strip() for line in expected_lines]

    assert actual_content == expected_content, f"\nExpected:\n{expected_content}\n\nGot:\n{actual_content}"
