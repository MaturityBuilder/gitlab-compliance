"""Branch-complete unit tests for ``src.compliance.lock_console``."""

from __future__ import annotations

from io import StringIO

from rich.console import Console

from src.compliance.lock_console import (
    _external_tree,
    _images_table,
    _includes_table,
    _inventory_health,
    _next_steps,
    _short_fingerprint,
    _unresolved_panel,
    render_fingerprint_line,
    render_lock_error,
    render_lock_report,
    run_with_progress,
)


def _console(**kwargs) -> Console:
    return Console(file=StringIO(), force_terminal=True, width=120, height=50, **kwargs)


def test_short_fingerprint_short_value():
    assert _short_fingerprint("sha256:abcd") == "sha256:abcd"


def test_inventory_health_letter_grades_and_fetch_gaps():
    # 60 + 40 = 100 → A
    assert (
        _inventory_health(
            {
                "includes": [{"resolved": True, "type": "local"}],
                "images": [],
                "unresolved": [],
                "externalSteps": [],
            }
        )["letter"]
        == "A"
    )

    # inventoried 2/3 ≈ 66.7% → 60 + 26.7 + 0 pin = 86.7 → B
    assert (
        _inventory_health(
            {
                "includes": [
                    {"resolved": True, "type": "local"},
                    {"resolved": True, "type": "local"},
                    {"resolved": False, "type": "project"},
                ],
                "images": [{"digest": ""}],
                "unresolved": [],
                "externalSteps": [],
            }
        )["letter"]
        == "B"
    )

    # Unresolved project only, no images → 60 + 0 = 60 → C
    assert (
        _inventory_health(
            {
                "includes": [{"resolved": False, "type": "project"}],
                "images": [],
                "unresolved": [],
                "externalSteps": [],
            }
        )["letter"]
        == "C"
    )

    # 60 + 0 pin - 8 fetch gap = 52 → D
    assert (
        _inventory_health(
            {
                "includes": [{"resolved": False, "type": "project"}],
                "images": [{"digest": ""}],
                "unresolved": [{"reason": "no_token"}],
                "externalSteps": [],
            }
        )["letter"]
        == "D"
    )

    # 60 - 30 = 30 → E
    assert (
        _inventory_health(
            {
                "includes": [{"resolved": False, "type": "project"}],
                "images": [{"digest": ""}],
                "unresolved": [
                    {"reason": "no_token"},
                    {"reason": "fetch_failed"},
                    {"reason": "fetch_failed"},
                    {"reason": "fetch_failed"},
                ],
                "externalSteps": [],
            }
        )["letter"]
        == "E"
    )


def test_includes_and_images_table_truncation_and_empty():
    includes = [
        {
            "type": "local",
            "project": f"f{i}.yml",
            "ref": "n/a",
            "resolved": i % 2 == 0,
            "contentHash": f"sha256:{'a' * 64}",
            "id": f"local:f{i}",
        }
        for i in range(10)
    ]
    table = _includes_table({"includes": includes}, verbose=False)
    assert table is not None
    assert table.caption is not None

    verbose = _includes_table({"includes": includes}, verbose=True)
    assert verbose is not None
    assert verbose.caption is None

    assert _includes_table({"includes": []}, verbose=False) is None
    assert _images_table({"images": []}, verbose=False) is None

    images = [
        {
            "source": "job",
            "parentJob": f"j{i}",
            "image": f"alpine:{i}",
            "digest": "sha256:x" if i % 2 else "",
        }
        for i in range(10)
    ]
    img_table = _images_table({"images": images}, verbose=False)
    assert img_table is not None
    assert img_table.caption is not None


def test_external_tree_overflow_and_unresolved_overflow():
    steps = [{"kind": "trigger", "id": f"trigger:job-{i}"} for i in range(8)]
    tree = _external_tree({"externalSteps": steps})
    assert tree is not None

    unresolved = [
        {"type": "project", "reference": f"p/{i}", "reason": "no_token"}
        for i in range(12)
    ]
    panel = _unresolved_panel({"unresolved": unresolved})
    assert panel is not None
    assert _unresolved_panel({"unresolved": []}) is None
    assert _external_tree({"externalSteps": []}) is None


def test_next_steps_branches():
    gen = _next_steps(
        command="generate",
        matches=None,
        pipeline_file="ci.yml",
        lock_file="lock",
    )
    assert gen is not None
    verified = _next_steps(
        command="verify",
        matches=True,
        pipeline_file="ci.yml",
        lock_file="lock",
    )
    assert verified is not None
    drift = _next_steps(
        command="verify",
        matches=False,
        pipeline_file="ci.yml",
        lock_file="lock",
    )
    assert drift is not None


def test_render_lock_report_update_quiet_drift_and_empty_inventory():
    lockfile = {
        "fingerprint": "sha256:" + ("f" * 64),
        "inventory": {
            "pipeline": {"jobs": []},
            "includes": [],
            "images": [],
            "externalSteps": [],
            "unresolved": [],
        },
    }
    console = _console()
    render_lock_report(
        command="update",
        lockfile=lockfile,
        pipeline_file="ci.yml",
        lock_file="l.lock",
        console=console,
    )
    assert "Inventory locked" in console.file.getvalue()

    quiet = Console(file=StringIO(), force_terminal=False)
    render_lock_report(
        command="verify",
        lockfile=lockfile,
        pipeline_file="ci.yml",
        lock_file="l.lock",
        matches=False,
        expected_fingerprint="sha256:old",
        actual_fingerprint="sha256:new",
        quiet=True,
        console=quiet,
    )
    assert "sha256:new" in quiet.file.getvalue()

    quiet_ok = Console(file=StringIO(), force_terminal=False)
    render_lock_report(
        command="verify",
        lockfile=lockfile,
        pipeline_file="ci.yml",
        lock_file="l.lock",
        matches=True,
        quiet=True,
        console=quiet_ok,
    )
    assert lockfile["fingerprint"] in quiet_ok.file.getvalue()


def test_render_fingerprint_json_and_error():
    console = Console(file=StringIO(), force_terminal=False)
    render_fingerprint_line(
        "sha256:abc",
        dotenv_file="lock.env",
        as_json=True,
        console=console,
    )
    assert '"fingerprint": "sha256:abc"' in console.file.getvalue()

    quiet = Console(file=StringIO(), force_terminal=False)
    render_fingerprint_line(
        "sha256:abc",
        dotenv_file="lock.env",
        quiet=True,
        console=quiet,
    )
    assert quiet.file.getvalue().strip() == "sha256:abc"

    err = _console()
    render_lock_error("boom", hint="try again", console=err)
    assert "boom" in err.file.getvalue()


def test_run_with_progress_terminal():
    console = _console()
    assert run_with_progress("scan", lambda: 7, console=console, quiet=False) == 7


def test_quiet_fingerprint_is_single_line_even_with_dotenv_path():
    quiet = Console(file=StringIO(), force_terminal=False)
    render_fingerprint_line(
        "sha256:abc",
        dotenv_file="lock.env",
        quiet=True,
        console=quiet,
    )
    assert quiet.file.getvalue().strip() == "sha256:abc"
