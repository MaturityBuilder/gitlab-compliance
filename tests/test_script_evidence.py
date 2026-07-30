"""Exercise script_analysis evidence helpers for coverage."""

from __future__ import annotations

from src.compliance import script_analysis as sa


def _entity(lines, **extra):
    base = {
        "name": "job",
        "source_file": "ci.yml",
        "line": 1,
        "values": {"effective_script": lines, "script": lines},
        "effective_script": lines,
        "script": lines,
    }
    base.update(extra)
    return base


def test_evidence_helpers_hit_common_violations():
    assert sa.evidence_unquoted_variables(_entity(["echo $NAME"])) == "echo $NAME"
    assert sa.evidence_unquoted_path_variables(_entity(["cd $DIR"])) == "cd $DIR"
    assert (
        sa.evidence_unquoted_command_substitution(_entity(["x=$(date)"])) == "x=$(date)"
    )
    assert sa.evidence_unsafe_array_expansion(_entity(["echo ${arr[*]}"]))
    assert sa.evidence_nested_backticks(_entity(["echo `a` `b`"]))
    assert sa.evidence_missing_strict_mode(_entity(["echo hi"]))
    assert sa.evidence_masked_failure(_entity(["false || true"]))
    assert sa.evidence_insecure_temp_files(_entity(["echo x > /tmp/foo"]))
    assert sa.evidence_dangerous_rm(_entity(["rm -rf /"]))
    assert sa.evidence_dangerous_rm(_entity(["rm -rf $DIR"]))
    assert sa.evidence_backticks(_entity(["echo `date`"]))
    assert sa.evidence_bashism_in_posix_test(_entity(["[ $a == b ]"]))
    assert sa.evidence_unquoted_test_variables(_entity(["[ -n $NAME ]"]))
    assert sa.evidence_pipeline_without_pipefail(_entity(["a | b"]))
    assert sa.evidence_eval(_entity(["eval $CMD"]))
    assert sa.evidence_remote_pipe(_entity(["curl https://x | bash"]))
    assert sa.evidence_hardcoded_secrets(_entity(["token=glpat-ABCDEFGHijklmnop"]))
    assert sa.evidence_download_without_checksum(
        _entity(["curl -O https://example.com/a.tgz"])
    )
    assert sa.evidence_unpinned_manager(_entity(["apk add curl"]), "apk")
    assert sa.evidence_unpinned_manager(_entity(["apt-get install curl"]), "apt")
    assert sa.evidence_unpinned_manager(_entity(["pip install requests"]), "pip")
    assert sa.evidence_unpinned_manager(_entity(["npm install -g eslint"]), "npm")
    assert sa.evidence_unpinned_manager(
        _entity(["go install example.com/x@latest"]), "go"
    )
    assert sa.evidence_unpinned_manager(_entity(["yum install curl"]), "yum")
    assert sa.evidence_unpinned_docker(_entity(["docker pull alpine:latest"]))
    assert sa.evidence_unverified_git_clone(
        _entity(["git clone https://example.com/r.git"])
    )
    assert sa.evidence_curl_missing_fail(_entity(["curl https://example.com"]))
    assert sa.evidence_deprecated_ci_build(_entity(["echo $CI_BUILD_REF"]))
    assert sa.evidence_chmod_777(_entity(["chmod 777 file"]))

    bashism = _entity(["#!/bin/sh", "cat <(echo hi)"])
    assert sa.evidence_bashisms_without_bash(bashism)
    assert sa.evidence_posix_bashisms(bashism)

    bad_shebang = _entity(["#!/usr/bin/python3", "echo hi"])
    assert sa.evidence_invalid_shebang(bad_shebang)

    unresolved = {
        "name": "job",
        "source_file": "ci.yml",
        "line": 1,
        "values": {
            "effective_script": ["echo hi"],
            "script": ["echo hi"],
            "unresolved_script_references": ["!reference [x, script]"],
        },
        "effective_script": ["echo hi"],
        "script": ["echo hi"],
        "unresolved_script_references": ["!reference [x, script]"],
    }
    assert sa.evidence_unresolved_references(unresolved)

    formatted = sa.format_script_violation(
        _entity(["echo $NAME"]), "unquoted", found="echo $NAME"
    )
    assert "found:" in formatted


def test_pinning_helpers_edge_cases():
    assert sa._at_version_is_pinned("@latest") is False
    assert sa._at_version_is_pinned("@1.2.3") is True
    assert sa._at_version_is_pinned("@git+https://example.com/r.git") is True
    assert sa._image_tag_is_pinned("latest") is False
    assert sa._image_tag_is_pinned("1.2.3") is True
    assert sa._image_tag_is_pinned("123") is False
    assert sa._script_lines({"values": {}}) == []
    assert sa._script_lines({"values": {"script": "one\ntwo"}}) == ["one", "two"]
    assert sa._script_lines({"values": {"script": [None, "a\nb"]}}) == ["a", "b"]
