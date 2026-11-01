"""Tests for dynamic child pipeline (trigger.include artifact) support."""

from __future__ import annotations

from pathlib import Path

from src.compliance.model import load_yaml_entities
from src.modules.pipeline_data import collect_pipeline_data


def _write(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8")
    return path


def test_artifact_present_merges_child_jobs(tmp_path: Path):
    generated = _write(
        tmp_path / "generated-config.yml",
        "child_job:\n  image: alpine:3.19\n  script: [echo child]\n",
    )
    parent = _write(
        tmp_path / ".gitlab-ci.yml",
        """
generate-config:
  script: [echo]
  artifacts:
    paths: [generated-config.yml]
child-pipeline:
  trigger:
    include:
      - artifact: generated-config.yml
        job: generate-config
""",
    )

    data = collect_pipeline_data(str(parent), detailed=True, include_scripts=True)
    names = {job["name"] for job in data["jobs"]}
    assert "child_job" in names
    child = next(job for job in data["jobs"] if job["name"] == "child_job")
    assert child["dynamic_parent_job"] == "child-pipeline"
    assert child["generated_artifact"] == "generated-config.yml"
    assert data["dynamic_child_pipelines"][0]["resolved"] is True
    assert not data["unresolved_includes"]
    assert generated.exists()


def test_artifact_missing_records_coverage_gap(tmp_path: Path):
    parent = _write(
        tmp_path / ".gitlab-ci.yml",
        """
child-pipeline:
  trigger:
    include:
      - artifact: generated-config.yml
        job: generate-config
""",
    )

    data = collect_pipeline_data(str(parent), detailed=True)
    assert {job["name"] for job in data["jobs"]} == {"child-pipeline"}
    assert data["dynamic_child_pipelines"][0]["resolved"] is False
    reasons = {item["reason"] for item in data["unresolved_includes"]}
    assert "generated_at_runtime" in reasons


def test_path_outside_project_rejected(tmp_path: Path):
    outside = tmp_path.parent / f"{tmp_path.name}-outside.yml"
    outside.write_text("evil:\n  script: [echo]\n", encoding="utf-8")
    parent = _write(
        tmp_path / ".gitlab-ci.yml",
        f"""
child-pipeline:
  trigger:
    include:
      - artifact: ../{outside.name}
        job: generate-config
""",
    )

    data = collect_pipeline_data(str(parent), detailed=True)
    assert "evil" not in {job["name"] for job in data["jobs"]}
    reasons = {item["reason"] for item in data["unresolved_includes"]}
    assert "path_rejected" in reasons
    outside.unlink(missing_ok=True)


def test_no_resolve_generated_leaves_child_out(tmp_path: Path):
    _write(
        tmp_path / "generated-config.yml",
        "child_job:\n  script: [echo child]\n",
    )
    parent = _write(
        tmp_path / ".gitlab-ci.yml",
        """
child-pipeline:
  trigger:
    include:
      - artifact: generated-config.yml
        job: generate-config
""",
    )

    data = collect_pipeline_data(str(parent), detailed=True, resolve_generated=False)
    assert {job["name"] for job in data["jobs"]} == {"child-pipeline"}
    assert data.get("dynamic_child_pipelines") == []
    assert data["unresolved_includes"] == []


def test_explicit_generated_config_loads_alternate_path(tmp_path: Path):
    alt = _write(tmp_path / "alt-generated.yml", "alt_job:\n  script: [echo alt]\n")
    parent = _write(tmp_path / ".gitlab-ci.yml", "root:\n  script: [echo root]\n")

    data = collect_pipeline_data(
        str(parent),
        detailed=True,
        generated_configs=[str(alt.name)],
    )
    names = {job["name"] for job in data["jobs"]}
    assert names == {"root", "alt_job"}
    assert data["dynamic_child_pipelines"][0]["resolved"] is True


def test_explicit_generated_config_dedupes_with_artifact(tmp_path: Path):
    generated = _write(
        tmp_path / "generated-config.yml",
        "child_job:\n  script: [echo child]\n",
    )
    parent = _write(
        tmp_path / ".gitlab-ci.yml",
        """
child-pipeline:
  trigger:
    include:
      - artifact: generated-config.yml
        job: generate-config
""",
    )

    data = collect_pipeline_data(
        str(parent),
        detailed=True,
        generated_configs=[str(generated.name)],
    )
    child_jobs = [job for job in data["jobs"] if job["name"] == "child_job"]
    assert len(child_jobs) == 1


def test_trigger_include_local_merges(tmp_path: Path):
    _write(tmp_path / "child-local.yml", "local_child:\n  script: [echo local]\n")
    parent = _write(
        tmp_path / ".gitlab-ci.yml",
        """
child:
  trigger:
    include:
      - local: child-local.yml
""",
    )

    data = collect_pipeline_data(str(parent), detailed=True)
    assert "local_child" in {job["name"] for job in data["jobs"]}
    record = data["dynamic_child_pipelines"][0]
    assert record["include_type"] == "local"
    assert record["resolved"] is True


def test_load_yaml_entities_exposes_dynamic_child_pipelines(tmp_path: Path):
    _write(
        tmp_path / "generated-config.yml",
        "child_job:\n  script: [echo child]\n",
    )
    parent = _write(
        tmp_path / ".gitlab-ci.yml",
        """
child-pipeline:
  trigger:
    include:
      - artifact: generated-config.yml
        job: generate-config
""",
    )

    entities, unresolved = load_yaml_entities(str(parent))
    assert unresolved == []
    dyn = entities["dynamic_child_pipelines"]
    assert len(dyn) == 1
    assert dyn[0]["type"] == "dynamic_child_pipeline"
    assert dyn[0]["trigger_job"] == "child-pipeline"
    assert dyn[0]["resolved"] is True
    child = next(job for job in entities["jobs"] if job["name"] == "child_job")
    assert child["values"]["dynamic_parent_job"] == "child-pipeline"
    assert child["values"]["generated_artifact"] == "generated-config.yml"
