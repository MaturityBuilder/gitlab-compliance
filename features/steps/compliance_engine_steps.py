import os
import subprocess
import sys

from behave import then, when


@when('I run basic compliance on "{pipeline}" with policies "{policy_dir}"')
def step_run_compliance(context, pipeline, policy_dir):
    _run_compliance(context, pipeline, policy_dir)


@when('I run api compliance on "{pipeline}" with policies "{policy_dir}"')
def step_run_api_compliance(context, pipeline, policy_dir):
    _run_compliance(context, pipeline, policy_dir)


@when('I run strict api compliance on "{pipeline}" with policies "{policy_dir}"')
def step_run_strict_api_compliance(context, pipeline, policy_dir):
    _run_compliance(context, pipeline, policy_dir, strict=True)


@when('I generate a compliance policy catalog from "{policy_dir}" to "{output_path}"')
def step_generate_policy_catalog(context, policy_dir, output_path):
    command = [
        sys.executable,
        "-m",
        "src.gitlab_docs",
        "compliance-doc",
        "-f",
        os.path.abspath(policy_dir),
        "-o",
        os.path.abspath(output_path),
    ]
    result = subprocess.run(command, capture_output=True, text=True, cwd=os.getcwd())
    context.compliance_exit_code = result.returncode
    context.compliance_output = result.stdout + result.stderr
    context.report_path = os.path.abspath(output_path)


@when(
    'I run compliance with format "{output_format}" on "{pipeline}" '
    'policies "{policy_dir}" to "{output_path}"'
)
def step_run_compliance_with_format(context, pipeline, policy_dir, output_format, output_path):
    _run_compliance(context, pipeline, policy_dir, output_format, output_path)


def _run_compliance(context, pipeline, policy_dir, output_format=None, output_path=None, strict=False):
    command = [
        sys.executable,
        "-m",
        "src.gitlab_docs",
        "compliance",
        "-f",
        os.path.abspath(policy_dir),
        "-p",
        os.path.abspath(pipeline),
    ]
    if strict:
        command.append("--strict")
    if output_format:
        command.extend(["--format", output_format])
    if output_path:
        command.extend(["-o", os.path.abspath(output_path)])
        context.report_path = os.path.abspath(output_path)

    result = subprocess.run(command, capture_output=True, text=True, cwd=os.getcwd())
    context.compliance_exit_code = result.returncode
    context.compliance_output = result.stdout + result.stderr


@then("compliance should pass")
def step_compliance_pass(context):
    assert context.compliance_exit_code == 0, context.compliance_output


@then("compliance should fail")
def step_compliance_fail(context):
    assert context.compliance_exit_code != 0, context.compliance_output


@then("compliance should pass with skipped scenarios")
def step_compliance_pass_skipped(context):
    assert context.compliance_exit_code == 0, context.compliance_output
    assert "skipped" in context.compliance_output.lower()


@then('compliance output should mention "{expected_text}"')
def step_compliance_output_mentions(context, expected_text):
    assert expected_text in context.compliance_output, context.compliance_output


@then("the report file should exist")
def step_report_exists(context):
    assert os.path.exists(context.report_path), f"Missing report: {context.report_path}"


@then('the report file should contain "{expected_text}"')
def step_report_contains(context, expected_text):
    with open(context.report_path, encoding="utf-8") as handle:
        content = handle.read()
    assert expected_text in content, content
