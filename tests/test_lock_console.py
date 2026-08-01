"""Tests for Rich lock console UX."""

from __future__ import annotations

from io import StringIO

from rich.console import Console

from src.compliance.lock_console import (
    _inventory_health,
    _short_fingerprint,
    collect_report_renderables,
    render_fingerprint_line,
    render_lock_report,
    run_with_progress,
)


def _sample_lockfile() -> dict:
    return {
        "fingerprint": "sha256:" + ("a" * 64),
        "inventory": {
            "pipeline": {"jobs": [{"name": "build"}, {"name": "test"}]},
            "includes": [
                {
                    "type": "local",
                    "project": "nested.yml",
                    "ref": "n/a",
                    "resolved": True,
                    "contentHash": "sha256:abc",
                },
                {
                    "type": "component",
                    "project": "https://gitlab.com/org/comp",
                    "ref": "1.0.0",
                    "resolved": False,
                },
            ],
            "images": [
                {
                    "source": "job",
                    "parentJob": "build",
                    "image": "alpine:3.19",
                    "digest": "",
                },
                {
                    "source": "service",
                    "parentJob": "build",
                    "image": "postgres:16@sha256:" + ("b" * 64),
                    "digest": "sha256:" + ("b" * 64),
                },
            ],
            "externalSteps": [
                {"kind": "component", "id": "component:org/comp@1.0.0"},
                {"kind": "trigger", "id": "trigger:deploy", "job": "deploy"},
            ],
            "unresolved": [
                {
                    "type": "component",
                    "reference": "https://gitlab.com/org/comp@1.0.0",
                    "reason": "unsupported_type",
                }
            ],
        },
    }


def test_short_fingerprint_truncates():
    full = "sha256:" + ("c" * 64)
    short = _short_fingerprint(full)
    assert short.startswith("sha256:")
    assert "…" in short
    assert len(short) < len(full)


def test_inventory_health_scores_sample():
    health = _inventory_health(_sample_lockfile()["inventory"])
    assert health["letter"] in {"A", "B", "C", "D", "E"}
    assert 0 <= health["score"] <= 100
    assert health["includeTotal"] == 2
    assert health["imageTotal"] == 2
    assert health["unresolved"] == 1


def test_render_lock_report_rich_output():
    console = Console(file=StringIO(), force_terminal=True, width=100, height=40)
    render_lock_report(
        command="generate",
        lockfile=_sample_lockfile(),
        pipeline_file=".gitlab-ci.yml",
        lock_file=".gitlab-ci.lock",
        console=console,
    )
    output = console.file.getvalue()
    assert "Inventory locked" in output
    assert "Coverage" in output
    assert "Includes" in output
    assert "Images" in output
    assert "Next steps" in output


def test_render_lock_report_drift_and_json():
    console = Console(file=StringIO(), force_terminal=True, width=100)
    lockfile = _sample_lockfile()
    render_lock_report(
        command="verify",
        lockfile=lockfile,
        pipeline_file=".gitlab-ci.yml",
        lock_file=".gitlab-ci.lock",
        matches=False,
        expected_fingerprint="sha256:expected",
        actual_fingerprint="sha256:actual",
        console=console,
    )
    text = console.file.getvalue()
    assert "Drift" in text or "drift" in text.lower()
    assert "sha256:expected" in text

    json_console = Console(file=StringIO(), force_terminal=False, width=80)
    render_lock_report(
        command="verify",
        lockfile=lockfile,
        pipeline_file=".gitlab-ci.yml",
        lock_file=".gitlab-ci.lock",
        matches=True,
        as_json=True,
        console=json_console,
    )
    payload = json_console.file.getvalue()
    assert '"matches": true' in payload
    assert '"fingerprint"' in payload


def test_render_fingerprint_and_progress():
    console = Console(file=StringIO(), force_terminal=True, width=80)
    render_fingerprint_line(
        "sha256:" + ("d" * 64),
        dotenv_file="lock.env",
        quiet=False,
        console=console,
    )
    assert "Fingerprint" in console.file.getvalue()

    quiet = Console(file=StringIO(), force_terminal=False)
    render_fingerprint_line("sha256:abc", quiet=True, console=quiet)
    assert quiet.file.getvalue().strip() == "sha256:abc"

    assert run_with_progress("work", lambda: 42, quiet=True) == 42


def test_collect_report_renderables():
    items = collect_report_renderables(
        command="generate",
        lockfile=_sample_lockfile(),
        pipeline_file=".gitlab-ci.yml",
        lock_file=".gitlab-ci.lock",
        verbose=True,
    )
    assert len(items) >= 3
