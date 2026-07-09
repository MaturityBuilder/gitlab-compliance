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

from src.compliance.api_enrichment import policies_require_api_enrichment
from src.compliance.builtin_policies import BUILTIN_POLICIES_DIR
from src.compliance.console import render_compliance_console
from src.compliance.metadata import (
    build_policy_catalog_from_dirs,
    iter_feature_files,
    normalize_scenario_name,
)
from src.compliance.models import ComplianceResult, ScenarioResult
from src.compliance.oci_registry import resolve_features_dir
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
    features_dir: str, with_builtin: bool = False
) -> list[str]:
    directories = []
    if with_builtin:
        directories.append(os.path.abspath(BUILTIN_POLICIES_DIR))
    directories.append(os.path.abspath(features_dir))
    return directories


def _collect_feature_files_from_dirs(features_dirs: list[str]) -> list[tuple[str, str]]:
    """Return (source_dir, feature_path) pairs from one or more policy roots."""
    collected: list[tuple[str, str]] = []
    for features_dir in features_dirs:
        for feature_file in _collect_feature_files(features_dir):
            collected.append((features_dir, feature_file))
    return collected


def _build_behave_workspace(features_dirs: list[str]) -> str:
    workspace = tempfile.mkdtemp(prefix="gitlab-compliance-compliance-")
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
    features_dir: str,
    pipeline_file: str,
    include_nested: bool = True,
    gitlab_url: str | None = None,
    token: str | None = None,
    project: str | None = None,
    group: str | None = None,
    strict: bool = False,
    dry_run: bool = False,
    output_format: str = "console",
    policies_source: str | None = None,
    policy_cache_dir: str | None = None,
    fix: bool = False,
    with_builtin: bool = False,
) -> ComplianceResult:
    policies_source = policies_source or features_dir
    resolved_features_dir = (
        resolve_features_dir(features_dir, cache_dir=policy_cache_dir)
        if not os.path.isdir(features_dir)
        else os.path.abspath(features_dir)
    )

    if not os.path.exists(pipeline_file):
        raise FileNotFoundError(f"Pipeline file not found: {pipeline_file}")

    if fix:
        if dry_run:
            raise ValueError("--fix cannot be used with --dry-run")
        if (
            not token
            and not os.getenv("GITLAB_TOKEN")
            and not os.getenv("CI_JOB_TOKEN")
        ):
            raise ValueError(
                "--fix requires a GitLab token (--token, GITLAB_TOKEN, or CI_JOB_TOKEN)"
            )
        from src.compliance.supply_chain_fix import apply_supply_chain_fixes

        apply_supply_chain_fixes(
            pipeline_file=pipeline_file,
            include_nested=include_nested,
            gitlab_url=gitlab_url,
            token=token or os.getenv("GITLAB_TOKEN") or os.getenv("CI_JOB_TOKEN") or "",
            project=project,
            group=group,
        )

    policy_directories = _resolve_policy_directories(
        resolved_features_dir, with_builtin=with_builtin
    )
    workspace = _build_behave_workspace(policy_directories)
    policy_catalog = build_policy_catalog_from_dirs(policy_directories)
    api_requirements = policies_require_api_enrichment(policy_directories)

    exit_code: int | None = None
    scenario_results: list[ScenarioResult] = []
    features = 0
    scenarios = 0
    passed = 0
    failed_count = 0
    skipped = 0

    try:
        with _temporary_gitlab_env(
            token=token,
            gitlab_url=gitlab_url,
            project=project,
            group=group,
        ):
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
                "gitlab_url": gitlab_url or "",
                "project": project or "",
                "group": group or "",
                "strict": "true" if strict else "false",
                "enrich_includes": (
                    "true" if (fix or api_requirements.enrich_includes) else "false"
                ),
                "enrich_images": (
                    "true" if (fix or api_requirements.enrich_images) else "false"
                ),
                "load_api_entities": (
                    "true" if (fix or api_requirements.load_api_entities) else "false"
                ),
            }

            runner = Runner(config)
            exit_code = runner.run()
            scenario_results = _collect_scenario_results(runner, policy_catalog)
            features = len(runner.features)
            all_scenarios = [
                scenario
                for feature in runner.features
                for scenario in _iter_feature_scenarios(feature)
            ]
            scenarios = len(all_scenarios)
            passed = sum(
                1 for scenario in all_scenarios if scenario.status.name == "passed"
            )
            failed_count = sum(
                1 for scenario in all_scenarios if scenario.status.name == "failed"
            )
            skipped = sum(
                1 for scenario in all_scenarios if scenario.status.name == "skipped"
            )
    finally:
        shutil.rmtree(workspace, ignore_errors=True)

    if output_format == "console":
        render_compliance_console(
            result=ComplianceResult(
                success=exit_code == 0,
                exit_code=exit_code,
                features=features,
                scenarios=scenarios,
                passed=passed,
                failed=failed_count,
                skipped=skipped,
                scenario_results=scenario_results,
            ),
            pipeline_file=pipeline_file,
            features_dir=policies_source,
        )
    else:
        logger.info(
            f"Compliance summary: {passed} passed, {failed_count} failed, {skipped} skipped "
            f"({scenarios} scenarios in {features} features)"
        )

    return ComplianceResult(
        success=exit_code == 0,
        exit_code=exit_code,
        features=features,
        scenarios=scenarios,
        passed=passed,
        failed=failed_count,
        skipped=skipped,
        scenario_results=scenario_results,
    )
