"""Unit tests for shell script compliance predicates."""

from __future__ import annotations

from src.compliance.script_analysis import (
    job_has_effective_script,
    script_curl_missing_fail,
    script_downloads_without_checksum,
    script_enables_strict_mode,
    script_has_dangerous_rm,
    script_has_hardcoded_secrets,
    script_has_pipefail,
    script_has_pipeline,
    script_has_remote_pipe_to_shell,
    script_has_unpinned_apk,
    script_has_unpinned_pip,
    script_has_unquoted_test_variables,
    script_has_unquoted_variables,
    script_shebang_is_valid,
    script_uses_backticks,
    script_uses_eval,
    script_uses_insecure_temp_files,
)


def _entity(lines):
    return {
        "name": "job",
        "source_file": "ci.yml",
        "line": 1,
        "values": {"effective_script": lines, "script": lines},
        "effective_script": lines,
        "script": lines,
    }


def test_unquoted_variables():
    assert script_has_unquoted_variables(_entity(["echo $FOO"]))
    assert not script_has_unquoted_variables(_entity(['echo "$FOO"']))


def test_remote_pipe_and_eval():
    assert script_has_remote_pipe_to_shell(_entity(["curl https://x | bash"]))
    assert script_uses_eval(_entity(['eval "$CMD"']))


def test_pinning_predicates():
    assert script_has_unpinned_apk(_entity(["apk add curl"]))
    assert not script_has_unpinned_apk(_entity(["apk add curl=8.5.0-r0"]))
    assert script_has_unpinned_pip(_entity(["pip install requests"]))
    assert not script_has_unpinned_pip(_entity(['pip install "requests==2.0"']))


def test_checksum_and_curl_fail():
    assert script_downloads_without_checksum(
        _entity(["curl -o file https://example.com/a.tgz"])
    )
    assert not script_downloads_without_checksum(
        _entity(
            [
                "curl -o file https://example.com/a.tgz",
                "sha256sum -c checksums",
            ]
        )
    )
    assert script_curl_missing_fail(_entity(["curl https://example.com"]))
    assert not script_curl_missing_fail(_entity(["curl -fsSL https://example.com"]))
    assert not script_curl_missing_fail(_entity(["apk add --no-cache curl=8.5.0-r0"]))
    assert not script_has_unquoted_test_variables(
        _entity(['if [ "$CI_COMMIT_SHA" = "abc" ]; then echo ok; fi'])
    )
    assert not script_has_unquoted_test_variables(
        _entity(['if [ "x $FOO" = "x bar" ]; then echo ok; fi'])
    )
    assert script_has_unquoted_test_variables(
        _entity(["if [ $FOO = bar ]; then echo x; fi"])
    )


def test_strict_mode_and_pipefail():
    assert script_enables_strict_mode(_entity(["set -euo pipefail", "echo hi"]))
    assert script_has_pipeline(_entity(["echo a | grep a"]))
    assert script_has_pipefail(_entity(["set -o pipefail", "echo a | cat"]))


def test_file_and_security():
    assert script_has_dangerous_rm(_entity(["rm -rf /"]))
    assert script_uses_insecure_temp_files(_entity(["echo x > /tmp/fixed"]))
    assert script_has_hardcoded_secrets(_entity(["token=glpat-ABCDEFGHijklmnop"]))
    assert script_uses_backticks(_entity(["x=`date`"]))


def test_shebang_and_effective_script():
    assert script_shebang_is_valid(_entity(["#!/usr/bin/env bash", "echo hi"]))
    assert not script_shebang_is_valid(_entity(["#!/usr/local/custom", "echo hi"]))
    assert job_has_effective_script(_entity(["echo hi"]))
    assert not job_has_effective_script(_entity([]))
