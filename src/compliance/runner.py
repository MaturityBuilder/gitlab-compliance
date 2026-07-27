"""Run GitLab compliance policy feature files."""

from __future__ import annotations

import contextlib
import os
import shutil
import tempfile

from behave.configuration import Configuration
from behave.model import ScenarioOutline
from behave.runner import Runner
from behave.step_registry import registry

from src.compliance.builtin_policies import (
    BUILTIN_POLICIES_DIR,
    BUILTIN_SHELL_POLICIES_DIR,
    BUILTIN_SUPPLY_CHAIN_POLICIES_DIR,
)
from src.compliance.console import print_error, render_compliance_console
from src.compliance.metadata import (
    PolicyRoot,
    discover_policies,
    iter_feature_files,
    normalize_scenario_name,
)
from src.compliance.models import ComplianceResult, ScenarioResult
from src.compliance.oci_registry import resolve_features_dir
from src.compliance.release_cache import ReleaseMetadataCache
from src.compliance.secret_redact import redact_secrets, token_is_ci_job_token
from src.modules.logging import logger

COMPLIANCE_SUPPORT_DIR = os.path.join(
    os.path.dirname(__file__),
    "behave_support",
)

ENVIRONMENT_STUB = """from src.compliance.behave_support.environment import *  # noqa: F401,F403
"""


@contextlib.contextmanager
def _temporary_gitlab_env(
    *,
    token: str | None,
    gitlab_url: str | None,
    project: str | None,
    group: str | None,
):
    """Inject GitLab credentials into the process env for the Behave subprocess."""
    updates: dict[str, str] = {}
    if token:
        updates["GITLAB_TOKEN"] = token
    if gitlab_url:
        updates["GITLAB_URL"] = gitlab_url
    if project:
        updates["CI_PROJECT_PATH"] = project
    if group:
        updates["GITLAB_GROUP_PATH"] = group

    previous: dict[str, str | None] = {}
    for key, value in updates.items():
        previous[key] = os.environ.get(key)
        os.environ[key] = value
    try:
        yield
    finally:
        for key, old_value in previous.items():
            if old_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = old_value


def _assert_within_directory(root: str, candidate: str) -> None:
    root_path = os.path.realpath(root)
    candidate_path = os.path.realpath(candidate)
    try:
        common = os.path.commonpath([root_path, candidate_path])
    except ValueError as exc:
        raise ValueError(f"Invalid feature file path: {candidate}") from exc
    if common != root_path:
        raise ValueError(f"Feature file escapes policies directory: {candidate}")


def _collect_feature_files(features_dir: str) -> list[str]:
    return list(iter_feature_files(features_dir))


def _resolve_policy_directories(
    features_dir: str | None,
    with_builtin: bool = False,
    with_shell_check: bool = False,
    with_supply_chain: bool = False,
) -> list[PolicyRoot]:
    roots: list[PolicyRoot] = []
    if with_builtin:
        roots.append(PolicyRoot(os.path.abspath(BUILTIN_POLICIES_DIR), recursive=False))
    if with_shell_check:
        shell_dir = os.path.abspath(BUILTIN_SHELL_POLICIES_DIR)
        if not any(root.path == shell_dir for root in roots):
            roots.append(PolicyRoot(shell_dir))
    if with_supply_chain:
        supply_dir = os.path.abspath(BUILTIN_SUPPLY_CHAIN_POLICIES_DIR)
        if not any(root.path == supply_dir for root in roots):
            roots.append(PolicyRoot(supply_dir))
    if features_dir:
        roots.append(PolicyRoot(os.path.abspath(features_dir)))
    if not roots:
        raise ValueError(
            "No policy source provided. Pass --features/-f and/or enable "
            "--with-builtin, --with-shell-check, or --with-supply-chain."
        )
    return roots


def resolve_policies_source_label(
    features_dir: str | None,
    *,
    with_builtin: bool = False,
    with_shell_check: bool = False,
    with_supply_chain: bool = False,
) -> str:
    if features_dir:
        return features_dir
    enabled = [
        label
        for flag, label in (
            (with_builtin, BUILTIN_POLICIES_DIR),
            (with_shell_check, BUILTIN_SHELL_POLICIES_DIR),
            (with_supply_chain, BUILTIN_SUPPLY_CHAIN_POLICIES_DIR),
        )
        if flag
    ]
    if not enabled:
        return BUILTIN_POLICIES_DIR
    if len(enabled) == 1:
        return enabled[0]
    return ", ".join(enabled)


def _collect_feature_files_from_dirs(features_dirs: list[str]) -> list[tuple[str, str]]:
    """Return (source_dir, feature_path) pairs from one or more policy roots."""
    collected: list[tuple[str, str]] = []
    seen_files: set[str] = set()
    for features_dir in features_dirs:
        for feature_file in _collect_feature_files(features_dir):
            real_path = os.path.realpath(feature_file)
            if real_path in seen_files:
                continue
            seen_files.add(real_path)
            collected.append((features_dir, feature_file))
    return collected


def _build_behave_workspace(
    features_dirs: list[str],
    collected: list[tuple[str, str]] | None = None,
) -> str:
    workspace = tempfile.mkdtemp(prefix="gitlab-compliance-compliance-")
    if collected is None:
        collected = _collect_feature_files_from_dirs(features_dirs)

    if not collected:
        raise FileNotFoundError(
            f"No .feature files found in policy directories: {features_dirs}"
        )

    seen_targets: set[str] = set()
    for source_dir, feature_file in collected:
        _assert_within_directory(source_dir, feature_file)
        rel_path = os.path.relpath(
            os.path.realpath(feature_file), os.path.realpath(source_dir)
        )
        if rel_path.startswith(".."):
            raise ValueError(f"Feature file escapes policies directory: {feature_file}")

        source_label = os.path.basename(source_dir.rstrip(os.sep))
        target_rel = (
            rel_path
            if len(features_dirs) == 1
            else os.path.join(source_label, rel_path)
        )
        if target_rel in seen_targets:
            base, ext = os.path.splitext(target_rel)
            target_rel = f"{base}__{source_label}{ext}"
        seen_targets.add(target_rel)

        target = os.path.join(workspace, target_rel)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        os.symlink(os.path.realpath(feature_file), target)

    with open(
        os.path.join(workspace, "environment.py"), "w", encoding="utf-8"
    ) as handle:
        handle.write(ENVIRONMENT_STUB)

    os.symlink(
        os.path.join(COMPLIANCE_SUPPORT_DIR, "steps"),
        os.path.join(workspace, "steps"),
    )
    return workspace


def _feature_name(feature) -> str:
    return os.path.basename(getattr(feature, "filename", "unknown.feature"))


def _feature_file_path(feature) -> str:
    return os.path.realpath(getattr(feature, "filename", ""))


def _scenario_message(scenario) -> str:
    for step in scenario.steps:
        if step.status.name == "failed" and step.error_message:
            return str(step.error_message)
    if getattr(scenario, "skip_reason", None):
        return str(scenario.skip_reason)
    if getattr(scenario, "error_message", None):
        return str(scenario.error_message)
    return ""


def _iter_feature_scenarios(feature) -> list:
    """Return executed scenarios, expanding Scenario Outline example rows."""
    expanded: list = []
    for run_item in feature.scenarios:
        if isinstance(run_item, ScenarioOutline):
            expanded.extend(run_item.scenarios)
        else:
            expanded.append(run_item)
    return expanded


def _collect_scenario_results(runner: Runner, policy_catalog) -> list[ScenarioResult]:
    results = []
    for feature in runner.features:
        feature_name = _feature_name(feature)
        feature_file = _feature_file_path(feature)
        for scenario in _iter_feature_scenarios(feature):
            annotation = policy_catalog.lookup_scenario(feature_file, scenario.name)
            custom = annotation.custom if annotation else {}
            message = _scenario_message(scenario)
            normalized = normalize_scenario_name(scenario.name)
            if scenario.name != normalized:
                message = (
                    f"{message} [{normalized}]"
                    if message
                    else f"Example row for: {normalized}"
                )
            results.append(
                ScenarioResult(
                    feature=feature_name,
                    name=scenario.name,
                    status=scenario.status.name,
                    message=message,
                    policy_id=annotation.policy_id if annotation else "",
                    title=annotation.title if annotation else scenario.name,
                    description=annotation.description if annotation else "",
                    severity=str(custom.get("severity", "")) if custom else "",
                )
            )
    return results


def run_compliance(
    features_dir: str | None,
    pipeline_file: str,
    include_nested: bool = True,
    max_include_depth: int | None = None,
    gitlab_url: str | None = None,
    token: str | None = None,
    project: str | None = None,
    group: str | None = None,
    strict: bool = False,
    dry_run: bool = False,
    output_format: str = "console",
    policies_source: str | None = None,
    policy_cache_dir: str | None = None,
    fix_supply_chain: bool = False,
    fix_policies: bool = False,
    with_builtin: bool = False,
    with_shell_check: bool = False,
    with_supply_chain: bool = False,
    create_mr: bool = False,
    post_mr_comment: bool = False,
    mr_iid: int | None = None,
    mr_branch: str | None = None,
    mr_target_branch: str | None = None,
    mr_comment_file: str | None = None,
) -> ComplianceResult:
    if not (features_dir or with_builtin or with_shell_check or with_supply_chain):
        raise ValueError(
            "No policy source provided. Pass --features/-f and/or enable "
            "--with-builtin, --with-shell-check, or --with-supply-chain."
        )

    policies_source = policies_source or resolve_policies_source_label(
        features_dir,
        with_builtin=with_builtin,
        with_shell_check=with_shell_check,
        with_supply_chain=with_supply_chain,
    )
    if features_dir:
        resolved_features_dir = (
            resolve_features_dir(features_dir, cache_dir=policy_cache_dir)
            if not os.path.isdir(features_dir)
            else os.path.abspath(features_dir)
        )
    else:
        resolved_features_dir = None

    if not os.path.exists(pipeline_file):
        raise FileNotFoundError(f"Pipeline file not found: {pipeline_file}")

    if create_mr and not (fix_supply_chain or fix_policies):
        raise ValueError(
            "--create-mr requires --fix-supply-chain and/or --fix-policies"
        )
    if create_mr and dry_run:
        raise ValueError("--create-mr cannot be used with --dry-run")
    if fix_supply_chain and dry_run:
        raise ValueError("--fix-supply-chain cannot be used with --dry-run")
    if fix_policies and dry_run:
        raise ValueError("--fix-policies cannot be used with --dry-run")

    resolved_token = (
        token or os.getenv("GITLAB_TOKEN") or os.getenv("CI_JOB_TOKEN") or ""
    )
    if fix_supply_chain and not resolved_token:
        raise ValueError(
            "--fix-supply-chain requires a GitLab token "
            "(--token, GITLAB_TOKEN, or CI_JOB_TOKEN)"
        )
    if fix_policies and not resolved_token:
        raise ValueError(
            "--fix-policies requires a GitLab token "
            "(--token, GITLAB_TOKEN, or CI_JOB_TOKEN)"
        )
    if create_mr and token_is_ci_job_token(resolved_token):
        raise ValueError(
            "--create-mr does not accept CI_JOB_TOKEN; set --token or GITLAB_TOKEN "
            "to a project or personal access token that can create branches and "
            "merge requests"
        )

    release_cache = ReleaseMetadataCache()
    fix_messages: list[str] = []
    if fix_supply_chain:
        from src.compliance.supply_chain_fix import apply_supply_chain_fixes

        fix_messages.extend(
            apply_supply_chain_fixes(
                pipeline_file=pipeline_file,
                include_nested=include_nested,
                max_include_depth=max_include_depth,
                gitlab_url=gitlab_url,
                token=resolved_token,
                project=project,
                group=group,
                cache=release_cache,
            )
        )

    policy_roots = _resolve_policy_directories(
        resolved_features_dir,
        with_builtin=with_builtin,
        with_shell_check=with_shell_check,
        with_supply_chain=with_supply_chain,
    )
    discovery = discover_policies(policy_roots)
    policy_catalog = discovery.catalog
    api_requirements = discovery.api_requirements
    workspace = _build_behave_workspace(
        [root.path for root in policy_roots], collected=discovery.feature_files
    )

    need_enrich_includes = (
        fix_supply_chain or fix_policies or api_requirements.enrich_includes
    )
    need_enrich_images = (
        fix_supply_chain or fix_policies or api_requirements.enrich_images
    )
    need_api_entities = fix_supply_chain or api_requirements.load_api_entities

    exit_code: int | None = None
    scenario_results: list[ScenarioResult] = []
    features = 0
    scenarios = 0
    passed = 0
    failed_count = 0
    skipped = 0

    def _run_behave() -> tuple[int, list[ScenarioResult], int, int, int, int, int]:
        registry.clear()
        argv = [
            "behave",
            workspace,
            "--no-capture",
            "--no-logcapture",
            "--no-summary",
            "--format",
            "null",
        ]
        if dry_run:
            argv.append("--dry-run")

        config = Configuration(argv)
        config.paths = [workspace]
        config.userdata = {
            "pipeline": os.path.abspath(pipeline_file),
            "include_nested": "true" if include_nested else "false",
            "max_include_depth": (
                "" if max_include_depth is None else str(max_include_depth)
            ),
            "gitlab_url": gitlab_url or "",
            "project": project or "",
            "group": group or "",
            "strict": "true" if strict else "false",
            "enrich_includes": "true" if need_enrich_includes else "false",
            "enrich_images": "true" if need_enrich_images else "false",
            "load_api_entities": "true" if need_api_entities else "false",
            "release_cache": release_cache,
        }

        runner = Runner(config)
        code = runner.run()
        results = _collect_scenario_results(runner, policy_catalog)
        feature_count = len(runner.features)
        all_scenarios = [
            scenario
            for feature in runner.features
            for scenario in _iter_feature_scenarios(feature)
        ]
        total = len(all_scenarios)
        passed_count = sum(
            1 for scenario in all_scenarios if scenario.status.name == "passed"
        )
        failed = sum(
            1 for scenario in all_scenarios if scenario.status.name == "failed"
        )
        skipped_count = sum(
            1 for scenario in all_scenarios if scenario.status.name == "skipped"
        )
        return (
            code,
            results,
            feature_count,
            total,
            passed_count,
            failed,
            skipped_count,
        )

    try:
        with _temporary_gitlab_env(
            token=token,
            gitlab_url=gitlab_url,
            project=project,
            group=group,
        ):
            if fix_policies:
                _probe_code, probe_results, *_rest = _run_behave()
                from src.compliance.policy_fix import apply_policy_remediations

                fix_messages.extend(
                    apply_policy_remediations(
                        probe_results,
                        pipeline_file=pipeline_file,
                        include_nested=include_nested,
                        max_include_depth=max_include_depth,
                        gitlab_url=gitlab_url,
                        token=resolved_token,
                        project=project,
                        group=group,
                        cache=release_cache,
                    )
                )

            (
                exit_code,
                scenario_results,
                features,
                scenarios,
                passed,
                failed_count,
                skipped,
            ) = _run_behave()
    finally:
        shutil.rmtree(workspace, ignore_errors=True)

    result = ComplianceResult(
        success=exit_code == 0,
        exit_code=exit_code if exit_code is not None else 1,
        features=features,
        scenarios=scenarios,
        passed=passed,
        failed=failed_count,
        skipped=skipped,
        scenario_results=scenario_results,
    )

    # Always emit the compliance report before optional GitLab side effects so a
    # failed --create-mr / --post-mr-comment cannot hide check results.
    if output_format == "console":
        render_compliance_console(
            result=result,
            pipeline_file=pipeline_file,
            features_dir=policies_source,
        )
    else:
        logger.info(
            f"Compliance summary: {passed} passed, {failed_count} failed, {skipped} skipped "
            f"({scenarios} scenarios in {features} features)"
        )

    side_effect_failed = False

    if create_mr:
        from src.compliance.merge_requests import create_supply_chain_merge_request

        try:
            create_supply_chain_merge_request(
                pipeline_file=pipeline_file,
                fix_messages=fix_messages,
                gitlab_url=gitlab_url,
                token=resolved_token,
                project=project,
                branch_name=mr_branch,
                target_branch=mr_target_branch,
            )
        except (ValueError, OSError) as exc:
            detail = redact_secrets(str(exc))
            print_error(detail, title="Merge request failed")
            logger.error("Merge request failed: %s", detail)
            side_effect_failed = True

    if post_mr_comment:
        from src.compliance.merge_requests import post_compliance_mr_comment
        from src.compliance.render import render_compliance_mr_comment

        try:
            if mr_comment_file:
                with open(mr_comment_file, encoding="utf-8") as handle:
                    comment_body = handle.read()
            else:
                comment_body = render_compliance_mr_comment(
                    result=result,
                    pipeline_file=pipeline_file,
                    features_dir=policies_source,
                )
            post_compliance_mr_comment(
                body=comment_body,
                gitlab_url=gitlab_url,
                token=resolved_token,
                project=project,
                mr_iid=mr_iid,
            )
        except (ValueError, OSError) as exc:
            detail = redact_secrets(str(exc))
            print_error(detail, title="MR comment failed")
            logger.error("MR comment failed: %s", detail)
            side_effect_failed = True

    # Report was already emitted; fail the process so CI notices GitLab side-effect errors.
    if side_effect_failed and result.exit_code == 0:
        return ComplianceResult(
            success=False,
            exit_code=2,
            features=result.features,
            scenarios=result.scenarios,
            passed=result.passed,
            failed=result.failed,
            skipped=result.skipped,
            scenario_results=result.scenario_results,
        )

    return result
