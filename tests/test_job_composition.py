"""Tests for GitLab CI job script composition."""

from __future__ import annotations

from pathlib import Path

from src.modules.common import EnvLoader, load_yml_documents
from src.modules.gitlab_reference import UnresolvedReference, resolve_reference_value
from src.modules.job_composition import compose_job_scripts
from src.modules.pipeline_data import collect_pipeline_data

FIXTURES = Path(__file__).parent / "fixtures" / "shell_check"


def test_reference_constructor_returns_marker():
    docs = load_yml_documents("x: !reference [.job, script]\n")
    assert isinstance(docs[0]["x"], UnresolvedReference)
    assert docs[0]["x"].path == (".job", "script")


def test_resolve_reference_value():
    registry = {".job": {"config": {"script": ["echo hi"]}}}
    ref = UnresolvedReference(path=(".job", "script"))
    assert resolve_reference_value(ref, registry) == ["echo hi"]
    missing = UnresolvedReference(path=(".missing", "script"))
    assert resolve_reference_value(missing, registry) is missing


def test_collect_pipeline_data_includes_scripts(tmp_path):
    pipeline = tmp_path / ".gitlab-ci.yml"
    pipeline.write_text(
        "job:\n  script:\n    - echo hi\n",
        encoding="utf-8",
    )
    data = collect_pipeline_data(str(pipeline), include_scripts=True)
    job = data["jobs"][0]
    assert job["script"] == ["echo hi"]


def test_collect_pipeline_data_composes_extends():
    data = collect_pipeline_data(
        str(FIXTURES / "extends-reference.yml"),
        include_scripts=True,
        resolve_job_composition=True,
    )
    jobs = {job["name"]: job for job in data["jobs"]}
    consumer = jobs["consumer"]
    assert 'echo "from helper"' in consumer["effective_script"] or any(
        "from helper" in line for line in consumer["effective_script"]
    )
    assert any("base" in line for line in consumer["script"])
    assert ".base" in consumer["extends_chain"]


def test_compose_job_scripts_cycle_raises():
    registry = {
        "a": {"config": {"extends": "b", "script": ["echo a"]}, "source_file": "a.yml"},
        "b": {"config": {"extends": "a", "script": ["echo b"]}, "source_file": "b.yml"},
    }
    try:
        compose_job_scripts("a", registry)
        assert False, "expected cycle error"
    except ValueError as exc:
        assert "Cycle" in str(exc)


def test_compose_prefers_same_file_extends_parent(tmp_path):
    from src.modules.job_composition import job_registry_key, register_job_entry

    file_a = str(tmp_path / "a.yml")
    file_b = str(tmp_path / "b.yml")
    registry: dict = {}
    register_job_entry(
        registry,
        job_name=".base",
        config={"script": ["echo from-a"]},
        source_file=file_a,
        line=1,
    )
    register_job_entry(
        registry,
        job_name=".base",
        config={"script": ["echo from-b"]},
        source_file=file_b,
        line=1,
    )
    register_job_entry(
        registry,
        job_name="child",
        config={"extends": ".base", "script": ["echo child"]},
        source_file=file_a,
        line=5,
    )
    effective = compose_job_scripts("child", registry, source_file=file_a)
    texts = [line.text for line in effective.script]
    assert "echo from-a" in texts
    assert "echo from-b" not in texts
    assert job_registry_key(file_a, ".base") in registry


def test_hidden_jobs_included_in_composition():
    data = collect_pipeline_data(
        str(FIXTURES / "bad-pipeline.yml"),
        resolve_job_composition=True,
    )
    names = {job["name"] for job in data["jobs"]}
    assert ".bad-template" in names
    assert "bad-job" in names
