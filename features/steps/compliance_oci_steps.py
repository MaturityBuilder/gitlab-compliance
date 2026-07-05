import os
import shutil

from behave import given, then, when

from src.compliance.oci_registry import (
    bundle_policies_dir,
    extract_policy_bundle,
    is_oci_reference,
)


@when('I bundle and extract policies from "{policy_dir}" to "{output_dir}"')
def step_bundle_and_extract(context, policy_dir, output_dir):
    output_dir = os.path.abspath(output_dir)
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    bundle_path = bundle_policies_dir(os.path.abspath(policy_dir))
    bundle_dir = os.path.dirname(bundle_path)
    try:
        extract_policy_bundle(bundle_path, output_dir)
        context.extracted_policy_dir = output_dir
    finally:
        shutil.rmtree(bundle_dir, ignore_errors=True)


@then('the extracted policies directory should contain "{filename}"')
def step_extracted_contains(context, filename):
    target = os.path.join(context.extracted_policy_dir, "security", filename)
    assert os.path.exists(target), f"Missing extracted policy file: {target}"


@when('I check whether "{value}" is an OCI reference')
def step_check_oci_reference(context, value):
    context.is_oci_reference = is_oci_reference(value)


@then("it should be an OCI reference")
def step_should_be_oci_reference(context):
    assert context.is_oci_reference is True


@then("it should not be an OCI reference")
def step_should_not_be_oci_reference(context):
    assert context.is_oci_reference is False
