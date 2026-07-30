"""Integration tests for 10-hop nested local-include shell-check fixtures."""

from __future__ import annotations

from pathlib import Path

from src.compliance.runner import run_compliance
from src.modules.pipeline_data import collect_pipeline_data

NESTED_10 = Path(__file__).resolve().parent / "fixtures" / "shell_check" / "nested-10"
HAPPY = NESTED_10 / "happy" / ".gitlab-ci.yml"
SAD = NESTED_10 / "sad" / ".gitlab-ci.yml"

EXPECTED_LOCAL_PATHS = {"layers/layer-01.yml"} | {
    f"layer-{n:02d}.yml" for n in range(2, 11)
}

EXPECTED_FAMILIES = (
    "GLCI-SHELL-QUOTE",
    "GLCI-SHELL-PIN",
)


def _job_names(data: dict) -> set[str]:
    return {job["name"] for job in data["jobs"]}


def _local_include_paths(data: dict) -> set[str]:
    return {
        item["project"] for item in data["includes"] if item["include_type"] == "local"
    }


def test_happy_resolves_leaf_through_10_hops():
    data = collect_pipeline_data(str(HAPPY), detailed=True, include_nested=True)
    jobs = _job_names(data)
    assert "root_job" in jobs
    assert "nested_leaf_happy" in jobs
    assert EXPECTED_LOCAL_PATHS <= _local_include_paths(data)
    by_name = {job["name"]: job for job in data["jobs"]}
    assert by_name["nested_leaf_happy"]["source_file"].endswith("layer-10.yml")


def test_sad_resolves_leaf_through_10_hops():
    data = collect_pipeline_data(str(SAD), detailed=True, include_nested=True)
    jobs = _job_names(data)
    assert "root_job" in jobs
    assert "nested_leaf_sad" in jobs
    assert EXPECTED_LOCAL_PATHS <= _local_include_paths(data)
    by_name = {job["name"]: job for job in data["jobs"]}
    assert by_name["nested_leaf_sad"]["source_file"].endswith("layer-10.yml")


def test_depth_cap_excludes_leaf():
    """max_include_depth=9 loads hops 1–9 but not hop 10 (leaf)."""
    data = collect_pipeline_data(
        str(HAPPY),
        detailed=True,
        include_nested=True,
        max_include_depth=9,
    )
    jobs = _job_names(data)
    assert "root_job" in jobs
    assert "nested_leaf_happy" not in jobs
    unresolved = data.get("unresolved_includes", [])
    assert any(item.get("reason") == "depth_exceeded" for item in unresolved)


def test_happy_shell_check_passes():
    result = run_compliance(
        features_dir=None,
        pipeline_file=str(HAPPY),
        with_shell_check=True,
        output_format="markdown",
    )
    assert result.failed == 0, [
        (s.policy_id, s.message)
        for s in result.scenario_results
        if s.status == "failed"
    ]
    assert result.passed > 0
    assert result.success


def test_sad_shell_check_fails_expected_families():
    result = run_compliance(
        features_dir=None,
        pipeline_file=str(SAD),
        with_shell_check=True,
        output_format="markdown",
    )
    assert result.failed > 0
    assert not result.success
    failed_ids = {
        s.policy_id
        for s in result.scenario_results
        if s.status == "failed" and s.policy_id
    }
    for family in EXPECTED_FAMILIES:
        assert any(
            pid.startswith(family) for pid in failed_ids
        ), f"expected failures in {family}, got {sorted(failed_ids)}"
