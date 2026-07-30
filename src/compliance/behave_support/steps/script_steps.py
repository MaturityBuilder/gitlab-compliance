"""Behave steps for GitLab CI embedded shell script policies."""

from __future__ import annotations

from behave import given, then, when

from src.compliance.behave_support.environment import _skip_remaining_steps
from src.compliance.script_analysis import (
    evidence_backticks,
    evidence_bashism_in_posix_test,
    evidence_bashisms_without_bash,
    evidence_chmod_777,
    evidence_curl_missing_fail,
    evidence_dangerous_rm,
    evidence_deprecated_ci_build,
    evidence_download_without_checksum,
    evidence_eval,
    evidence_hardcoded_secrets,
    evidence_insecure_temp_files,
    evidence_invalid_shebang,
    evidence_masked_failure,
    evidence_missing_strict_mode,
    evidence_nested_backticks,
    evidence_pipeline_without_pipefail,
    evidence_posix_bashisms,
    evidence_remote_pipe,
    evidence_unpinned_docker,
    evidence_unpinned_manager,
    evidence_unquoted_command_substitution,
    evidence_unquoted_path_variables,
    evidence_unquoted_test_variables,
    evidence_unquoted_variables,
    evidence_unresolved_references,
    evidence_unsafe_array_expansion,
    evidence_unverified_git_clone,
    format_script_violation,
    job_has_effective_script,
    job_has_script_field,
    script_bashisms_without_bash_shebang,
    script_curl_missing_fail,
    script_defines_functions,
    script_downloads_without_checksum,
    script_enables_strict_mode,
    script_functions_mask_failures,
    script_has_bashism_in_posix_test,
    script_has_chmod_777,
    script_has_dangerous_rm,
    script_has_hardcoded_secrets,
    script_has_nested_backticks,
    script_has_pipefail,
    script_has_pipeline,
    script_has_remote_pipe_to_shell,
    script_has_shebang,
    script_has_unpinned_apk,
    script_has_unpinned_apt,
    script_has_unpinned_docker_image,
    script_has_unpinned_go_install,
    script_has_unpinned_npm,
    script_has_unpinned_pip,
    script_has_unpinned_yum,
    script_has_unquoted_command_substitution,
    script_has_unquoted_path_variables,
    script_has_unquoted_test_variables,
    script_has_unquoted_variables,
    script_has_unresolved_references,
    script_has_unsafe_array_expansion,
    script_has_unverified_git_clone,
    script_is_multiline,
    script_masks_failures,
    script_posix_shebang_with_bashisms,
    script_shebang_is_valid,
    script_uses_backticks,
    script_uses_eval,
    script_uses_insecure_temp_files,
)
from src.compliance.stash import filter_entities, name_starts_with


def _shell_check_verbose(context) -> bool:
    config = getattr(context, "config", None)
    userdata = getattr(config, "userdata", None) if config is not None else None
    if not isinstance(userdata, dict):
        return False
    return str(userdata.get("shell_check_verbose", "false")).lower() in {
        "true",
        "1",
        "yes",
        "on",
    }


def _set_stash(context, entities: list[dict]):
    context.stash = list(entities)
    context.step_mode = "given"
    context.scenario_skipped = False


def _set_stash_or_skip(context, entities: list[dict], *, skip_reason: str):
    if not entities:
        _skip_remaining_steps(context, skip_reason)
        return
    _set_stash(context, entities)


def _apply_filter(context, entities: list[dict], reason: str):
    if context.scenario_skipped:
        return
    context.step_mode = "when"
    if not entities:
        _skip_remaining_steps(context, reason)
        return
    context.stash = entities


def _assert_none(context, predicate, message: str, evidence=None):
    if context.scenario_skipped:
        return
    context.step_mode = "then"
    if not context.stash:
        raise AssertionError("No entities in stash to assert against.")
    verbose = _shell_check_verbose(context)
    failures = []
    for entity in context.stash:
        if not predicate(entity):
            continue
        found = evidence(entity) if verbose and evidence is not None else None
        failures.append(format_script_violation(entity, message, found=found))
    if failures:
        raise AssertionError("; ".join(failures))


def _assert_all_true(context, predicate, message: str, evidence=None):
    if context.scenario_skipped:
        return
    context.step_mode = "then"
    if not context.stash:
        raise AssertionError("No entities in stash to assert against.")
    verbose = _shell_check_verbose(context)
    failures = []
    for entity in context.stash:
        if predicate(entity):
            continue
        found = evidence(entity) if verbose and evidence is not None else None
        failures.append(format_script_violation(entity, message, found=found))
    if failures:
        raise AssertionError("; ".join(failures))


@given("I have any job with effective script defined")
def given_any_job_with_effective_script(context):
    jobs = filter_entities(
        context.compliance_entities.get("jobs", []),
        job_has_effective_script,
    )
    _set_stash_or_skip(
        context, jobs, skip_reason="No jobs with effective script found in pipeline"
    )


@given("I have any job with before_script defined")
def given_any_job_with_before_script(context):
    jobs = filter_entities(
        context.compliance_entities.get("jobs", []),
        lambda entity: job_has_script_field(entity, "before_script"),
    )
    _set_stash_or_skip(
        context, jobs, skip_reason="No jobs with before_script found in pipeline"
    )


@given("I have any job with script defined")
def given_any_job_with_script(context):
    jobs = filter_entities(
        context.compliance_entities.get("jobs", []),
        lambda entity: job_has_script_field(entity, "script"),
    )
    _set_stash_or_skip(
        context, jobs, skip_reason="No jobs with script found in pipeline"
    )


@when("a variable is expanded within a command")
def when_variable_expanded(context):
    filtered = filter_entities(context.stash, script_has_unquoted_variables)
    # Keep jobs that have expansions to validate; if none, keep stash for positive pass.
    if filtered:
        _apply_filter(context, filtered, "No jobs with variable expansions")
    else:
        context.step_mode = "when"


@when("variables are used as part of a path")
def when_variables_in_path(context):
    filtered = filter_entities(context.stash, script_has_unquoted_path_variables)
    if filtered:
        _apply_filter(context, filtered, "No jobs with path variable usage")
    else:
        context.step_mode = "when"


@when("command substitution is used")
def when_command_substitution(context):
    filtered = filter_entities(
        context.stash,
        lambda e: script_has_unquoted_command_substitution(e)
        or "$(" in str(e.get("values", {}).get("effective_script", "")),
    )
    if not filtered:
        filtered = filter_entities(
            context.stash,
            lambda e: "$("
            in "\n".join(
                map(str, e.get("values", {}).get("effective_script", []) or [])
            )
            or "`"
            in "\n".join(
                map(str, e.get("values", {}).get("effective_script", []) or [])
            ),
        )
    if filtered:
        _apply_filter(context, filtered, "No jobs with command substitution")
    else:
        context.step_mode = "when"


@when("an array is expanded")
def when_array_expanded(context):
    filtered = filter_entities(context.stash, script_has_unsafe_array_expansion)
    if filtered:
        _apply_filter(context, filtered, "No jobs with array expansions")
    else:
        context.step_mode = "when"


@when("the effective script has more than 1 line")
def when_multiline_script(context):
    filtered = filter_entities(context.stash, script_is_multiline)
    _apply_filter(context, filtered, "No multi-line effective scripts")


@when("rm is used recursively")
def when_rm_recursive(context):
    filtered = filter_entities(context.stash, script_has_dangerous_rm)
    if filtered:
        _apply_filter(context, filtered, "No recursive rm usage")
    else:
        context.step_mode = "when"


@when("a pipeline is used")
def when_pipeline_used(context):
    filtered = filter_entities(context.stash, script_has_pipeline)
    _apply_filter(context, filtered, "No pipelines found in scripts")


@when("temporary files are required")
def when_temp_files_required(context):
    filtered = filter_entities(context.stash, script_uses_insecure_temp_files)
    if filtered:
        _apply_filter(context, filtered, "No temporary file usage detected")
    else:
        context.step_mode = "when"


@when('its name starts with "{prefix}"')
def when_name_starts_with_prefix(context, prefix):
    filtered = filter_entities(context.stash, lambda e: name_starts_with(e, prefix))
    _apply_filter(context, filtered, f"No entity names start with '{prefix}'")


@then("the variable must be wrapped in double quotes")
def then_variables_quoted(context):
    _assert_none(
        context,
        script_has_unquoted_variables,
        "Unquoted variable expansions found",
        evidence=evidence_unquoted_variables,
    )


@then("all variables must be safely quoted")
def then_path_variables_quoted(context):
    _assert_none(
        context,
        script_has_unquoted_path_variables,
        "Unquoted variables used in file paths",
        evidence=evidence_unquoted_path_variables,
    )


@then("the result must be quoted unless word splitting is intended")
def then_cmd_sub_quoted(context):
    _assert_none(
        context,
        script_has_unquoted_command_substitution,
        "Unquoted command substitution found",
        evidence=evidence_unquoted_command_substitution,
    )


@then('array "@" syntax must be used where appropriate')
def then_array_at_syntax(context):
    _assert_none(
        context,
        script_has_unsafe_array_expansion,
        "Unsafe array expansion found",
        evidence=evidence_unsafe_array_expansion,
    )


@then("the script must enable strict mode options")
def then_strict_mode_table(context):
    _assert_all_true(
        context,
        script_enables_strict_mode,
        "Multi-line script missing set -e/-u/pipefail",
        evidence=evidence_missing_strict_mode,
    )


@then("failure must be handled explicitly")
def then_failure_handled(context):
    # With strict mode, failures are handled; otherwise flag || true masking.
    def ok(entity):
        if script_enables_strict_mode(entity):
            return True
        return not script_masks_failures(entity)

    _assert_all_true(
        context,
        ok,
        "Command failures are not handled explicitly",
        evidence=evidence_masked_failure,
    )


@then("functions must propagate failures")
def then_functions_propagate(context):
    filtered = filter_entities(context.stash, script_defines_functions)
    if not filtered:
        context.step_mode = "then"
        return
    context.stash = filtered
    _assert_none(
        context,
        script_functions_mask_failures,
        "Functions mask failures with || true",
        evidence=evidence_masked_failure,
    )


@then("file paths must be quoted")
def then_file_paths_quoted(context):
    _assert_none(
        context,
        script_has_unquoted_path_variables,
        "Unquoted file paths found",
        evidence=evidence_unquoted_path_variables,
    )


@then("mktemp must be used for temporary files")
def then_mktemp_used(context):
    _assert_none(
        context,
        script_uses_insecure_temp_files,
        "Insecure temporary file creation without mktemp",
        evidence=evidence_insecure_temp_files,
    )


@then("path validation must be performed for recursive rm")
def then_rm_protected(context):
    _assert_none(
        context,
        script_has_dangerous_rm,
        "Dangerous recursive rm without path validation",
        evidence=evidence_dangerous_rm,
    )


@then("command substitution must use dollar parentheses")
def then_no_backticks(context):
    _assert_none(
        context,
        script_uses_backticks,
        "Legacy backtick substitution found",
        evidence=evidence_backticks,
    )


@then("nested command substitution must use dollar parentheses")
def then_nested_dollar(context):
    _assert_none(
        context,
        script_has_nested_backticks,
        "Nested backtick substitution found",
        evidence=evidence_nested_backticks,
    )


@then("POSIX compliant operators must be used")
def then_posix_operators(context):
    _assert_none(
        context,
        script_has_bashism_in_posix_test,
        "Non-portable operators in [ tests",
        evidence=evidence_bashism_in_posix_test,
    )


@then("variables in test expressions must be quoted")
def then_test_vars_quoted(context):
    _assert_none(
        context,
        script_has_unquoted_test_variables,
        "Unquoted variables in test expressions",
        evidence=evidence_unquoted_test_variables,
    )


@then("pipefail must be enabled")
def then_pipefail(context):
    _assert_all_true(
        context,
        lambda e: (not script_has_pipeline(e)) or script_has_pipefail(e),
        "Pipeline used without pipefail",
        evidence=evidence_pipeline_without_pipefail,
    )


@then("eval must not be used")
def then_no_eval(context):
    _assert_none(
        context, script_uses_eval, "eval is used in script", evidence=evidence_eval
    )


@then("untrusted remote scripts must not be executed")
def then_no_remote_pipe(context):
    _assert_none(
        context,
        script_has_remote_pipe_to_shell,
        "Remote pipe to shell (curl|sh) detected",
        evidence=evidence_remote_pipe,
    )


@then("user supplied variables must be quoted or validated")
def then_user_input_safe(context):
    _assert_none(
        context,
        script_has_unquoted_variables,
        "User/CI variables used without quoting",
        evidence=evidence_unquoted_variables,
    )


@then("hardcoded secrets must not be present")
def then_no_secrets(context):
    _assert_none(
        context,
        script_has_hardcoded_secrets,
        "Hardcoded secret pattern detected",
        evidence=evidence_hardcoded_secrets,
    )


@then("script downloads must verify checksums")
def then_downloads_checksum(context):
    _assert_none(
        context,
        script_downloads_without_checksum,
        "Download without nearby checksum verification",
        evidence=evidence_download_without_checksum,
    )


@then('package installs of type "{manager}" must use pinned versions')
def then_packages_pinned(context, manager):
    predicates = {
        "apk": script_has_unpinned_apk,
        "pip": script_has_unpinned_pip,
        "apt": script_has_unpinned_apt,
        "yum": script_has_unpinned_yum,
        "npm": script_has_unpinned_npm,
        "go": script_has_unpinned_go_install,
    }
    predicate = predicates.get(manager)
    if predicate is None:
        raise AssertionError(f"Unknown package manager '{manager}'")
    _assert_none(
        context,
        predicate,
        f"Unpinned {manager} package install",
        evidence=lambda entity: evidence_unpinned_manager(entity, manager),
    )


@then("docker commands must pin container images to a tag or sha256 digest")
def then_docker_images_pinned(context):
    _assert_none(
        context,
        script_has_unpinned_docker_image,
        "Docker command references an unpinned container image",
        evidence=evidence_unpinned_docker,
    )


@then("git clone must verify commit or tag")
def then_git_clone_verified(context):
    _assert_none(
        context,
        script_has_unverified_git_clone,
        "git clone without commit/tag verification",
        evidence=evidence_unverified_git_clone,
    )


@then("curl must use fail flag")
def then_curl_fail(context):
    _assert_none(
        context,
        script_curl_missing_fail,
        "curl without --fail/-f",
        evidence=evidence_curl_missing_fail,
    )


@then("deprecated CI_BUILD variables must not be used")
def then_no_ci_build(context):
    from src.compliance.script_analysis import script_uses_deprecated_ci_build_vars

    _assert_none(
        context,
        script_uses_deprecated_ci_build_vars,
        "Deprecated $CI_BUILD_* variable used",
        evidence=evidence_deprecated_ci_build,
    )


@then("unresolved script references must not be present")
def then_no_unresolved_refs(context):
    _assert_none(
        context,
        script_has_unresolved_references,
        "Unresolved !reference in script blocks",
        evidence=evidence_unresolved_references,
    )


@then("shebang must be valid when present")
def then_shebang_valid(context):
    _assert_all_true(
        context,
        lambda e: (not script_has_shebang(e)) or script_shebang_is_valid(e),
        "Invalid shebang in script block",
        evidence=evidence_invalid_shebang,
    )


@then("bash specific features must declare bash")
def then_bash_declared(context):
    _assert_none(
        context,
        script_bashisms_without_bash_shebang,
        "Bash-specific syntax without bash shebang",
        evidence=evidence_bashisms_without_bash,
    )


@then("POSIX shebang scripts must not use bashisms")
def then_posix_no_bashisms(context):
    _assert_none(
        context,
        script_posix_shebang_with_bashisms,
        "Bashisms used with sh shebang",
        evidence=evidence_posix_bashisms,
    )


@then("chmod 777 must not be used")
def then_no_chmod_777(context):
    _assert_none(
        context,
        script_has_chmod_777,
        "chmod 777 is used",
        evidence=evidence_chmod_777,
    )
