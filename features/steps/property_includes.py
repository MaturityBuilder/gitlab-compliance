# import os
# import tempfile
# import yaml
# from behave import given, when, then
# from src.properties.includes import document_includes

# @given("a valid GLDOCS config file with project includes")
# def step_impl(context):
#     context.temp_dir = tempfile.TemporaryDirectory()
#     context.output_file = os.path.join(context.temp_dir.name, "README.md")
#     context.config_file = os.path.join(context.temp_dir.name, "config.yml")

#     config_data = {
#         "include": [
#             {
#                 "project": "test/project",
#                 "ref": "1.0.0",
#                 "file": "README.md",
#                 "variables": {"var": "value"},
#                 "rules": ["rule1"]
#             }
#         ]
#     }

#     with open(context.config_file, "w") as f:
#         yaml.dump(config_data, f)

# @given("README.md does not exist")
# def step_impl(context):
#     if os.path.exists(context.output_file):
#         os.remove(context.output_file)

# @when("I run the document_includes function")
# def step_impl(context):
#     document_includes(
#         OUTPUT_FILE=context.output_file,
#         GLDOCS_CONFIG_FILE=context.config_file,
#         DISABLE_TITLE=True,
#         DISABLE_TYPE_HEADING=True
#     )

# @then("the README.md file should contain the includes table")
# def step_impl(context):
#     assert os.path.exists(context.output_file), "README.md was not created"

#     with open(context.output_file, "r") as f:
#         content = f.read()

#     assert "Includes" in content
#     assert "test/project" in content
