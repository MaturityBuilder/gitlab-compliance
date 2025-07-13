import os
from behave import given, when, then
from src.modules.doc_controller import update_marked_block, marker_start, marker_end, file_path

@given('the file "README.md" does not exist')
def step_remove_file(context):
    if os.path.exists(file_path):
        os.remove(file_path)

@given('the file "README.md" contains the block')
def step_file_with_old_block(context):
    content = context.text.strip()
    block = f"{marker_start}\n{content}\n{marker_end}\n"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(block)

@when('I update the block with')
def step_update_block(context):
    update_marked_block(context.text)

@when('I dry-run update the block with')
def step_update_block_dry(context):
    os.environ["DRY_MODE"] = "1"
    update_marked_block(context.text)
    os.environ.pop("DRY_MODE", None)

@then('the file "README.md" should contain the marked block with')
def step_file_should_contain(context):
    expected_content = context.text.strip()
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    expected_block = f"{marker_start}\n{expected_content}\n{marker_end}"
    assert expected_block in content, f"Expected block not found in file. Got:\n{content}"
