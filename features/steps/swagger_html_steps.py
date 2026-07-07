import os

from behave import given, then, when
from click.testing import CliRunner

from src.gitlab_compliance import generate
from src.modules.pipeline_data import collect_pipeline_data
from src.modules.swagger_html import render_swagger_html


@given('a gitlab-ci config at "{config_path}"')
def step_gitlab_ci_config(context, config_path):
    context.config_path = config_path


@when('I generate swagger HTML to "{output_path}"')
def step_generate_swagger_html(context, output_path):
    context.output_path = output_path
    pipeline_data = collect_pipeline_data(context.config_path, detailed=False)
    html_output = render_swagger_html(pipeline_data)
    with open(output_path, "w", encoding="utf-8") as output_file:
        output_file.write(html_output)


@when('I generate detailed swagger HTML to "{output_path}"')
def step_generate_detailed_swagger_html(context, output_path):
    context.output_path = output_path
    pipeline_data = collect_pipeline_data(context.config_path, detailed=True)
    html_output = render_swagger_html(pipeline_data)
    with open(output_path, "w", encoding="utf-8") as output_file:
        output_file.write(html_output)


@when('I run generate with format "{output_format}" to "{output_path}"')
def step_run_generate_with_format(context, output_format, output_path):
    context.output_path = output_path
    runner = CliRunner()
    result = runner.invoke(
        generate,
        [
            "--format",
            output_format,
            "--input-config",
            context.config_path,
            "--output-file",
            output_path,
        ],
    )
    assert result.exit_code == 0, result.output


@then("the HTML file should exist")
def step_html_file_exists(context):
    assert os.path.exists(context.output_path)


@then('the HTML file should contain "{expected_text}"')
def step_html_contains(context, expected_text):
    with open(context.output_path, encoding="utf-8") as output_file:
        content = output_file.read()
    assert expected_text in content
