"""Run GitLab compliance policy feature files."""

from __future__ import annotations

import os
import shutil
import tempfile

from behave.configuration import Configuration
from behave.runner import Runner
from behave.step_registry import registry

from src.compliance.console import render_compliance_console
from src.compliance.metadata import build_policy_catalog
from src.compliance.models import ComplianceResult, ScenarioResult
from src.compliance.oci_registry import resolve_features_dir
from src.modules.logging import logger

COMPLIANCE_SUPPORT_DIR = os.path.join(
    os.path.dirname(__file__),
    "behave_support",
)

ENVIRONMENT_STUB = """from src.compliance.behave_support.environment import *  # noqa: F401,F403
"""


def _collect_feature_files(features_dir: str) -> list[str]:
    feature_files = []
    for root, _dirs, files in os.walk(features_dir):
        for filename in files:
            if filename.endswith(".feature"):
                feature_files.append(os.path.join(root, filename))
    return feature_files


def _build_behave_workspace(features_dir: str) -> str:
    workspace = tempfile.mkdtemp(prefix="gitlab-docs-compliance-")
    feature_files = _collect_feature_files(features_dir)

    if not feature_files:
        raise FileNotFoundError(f"No .feature files found in {features_dir}")

    for feature_file in feature_files:
        rel_path = os.path.relpath(feature_file, features_dir)
        target = os.path.join(workspace, rel_path)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        os.symlink(os.path.abspath(feature_file), target)

    with open(os.path.join(workspace, "environment.py"), "w", encoding="utf-8") as handle:
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


def _collect_scenario_results(runner: Runner, policy_catalog) -> list[ScenarioResult]:
    results = []
    for feature in runner.features:
        feature_name = _feature_name(feature)
        feature_file = _feature_file_path(feature)
        for scenario in feature.scenarios:
            annotation = policy_catalog.lookup_scenario(feature_file, scenario.name)
            results.append(
                ScenarioResult(
                    feature=feature_name,
                    name=scenario.name,
                    status=scenario.status.name,
                    message=_scenario_message(scenario),
                    policy_id=annotation.policy_id if annotation else "",
                    title=annotation.title if annotation else scenario.name,
                    description=annotation.description if annotation else "",
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
) -> ComplianceResult:
    policies_source = policies_source or features_dir
    resolved_features_dir = (
        resolve_features_dir(features_dir, cache_dir=policy_cache_dir)
        if not os.path.isdir(features_dir)
        else os.path.abspath(features_dir)
    )

    if not os.path.exists(pipeline_file):
        raise FileNotFoundError(f"Pipeline file not found: {pipeline_file}")

    workspace = _build_behave_workspace(resolved_features_dir)
    policy_catalog = build_policy_catalog(resolved_features_dir)

    try:
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
            "token": token or "",
            "project": project or "",
            "group": group or "",
            "strict": "true" if strict else "false",
        }

        runner = Runner(config)
        exit_code = runner.run()
        scenario_results = _collect_scenario_results(runner, policy_catalog)
        features = len(runner.features)
        scenarios = sum(len(feature.scenarios) for feature in runner.features)
        passed = sum(
            1 for feature in runner.features for scenario in feature.scenarios
            if scenario.status.name == "passed"
        )
        failed_count = sum(
            1 for feature in runner.features for scenario in feature.scenarios
            if scenario.status.name == "failed"
        )
        skipped = sum(
            1 for feature in runner.features for scenario in feature.scenarios
            if scenario.status.name == "skipped"
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
