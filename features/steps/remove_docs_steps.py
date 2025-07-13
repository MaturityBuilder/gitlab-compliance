import os
from tempfile import NamedTemporaryFile
from behave import given, when, then
from src.modules.reset_docs import gitlab_docs_remove_docs

GLDOCS_TITLE = "[comment]: <> (gitlab-docs-opening-auto-generated)"
GLDOCS_END = "[comment]: <> (gitlab-docs-closing-auto-generated)"

@given("a file with content between the markers")
def step_given_file_with_docs(context):
    context.temp_file = NamedTemporaryFile(delete=False, mode="w+", suffix=".md")
    context.temp_file.write("Header info\n")
    context.temp_file.write(GLDOCS_TITLE)
    context.temp_file.write("This is a doc block.\nMore doc lines.\n")
    context.temp_file.write(GLDOCS_END)
    context.temp_file.write("Footer info\n")
    context.temp_file.close()

@when("the gitlab_docs_remove_docs function is called")
def step_when_remove_docs_called(context):
    gitlab_docs_remove_docs(context.temp_file.name, GLDOCS_TITLE, GLDOCS_END)

@then("the file should contain only content outside the markers")
def step_then_check_file_contents(context):
    with open(context.temp_file.name, "r") as f:
        print("MY Output")
        print(f.read())
        result = f.read()
    expected = "Header info\n" + GLDOCS_TITLE + GLDOCS_END + "Footer info\n"
    assert result == expected
    os.unlink(context.temp_file.name)
