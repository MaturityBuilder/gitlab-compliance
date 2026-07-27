"""Extra coverage for shell script validation modules."""

from __future__ import annotations

from types import SimpleNamespace

from src.compliance.behave_support.steps import script_steps as steps
from src.compliance.script_analysis import (
    format_script_violation,
    job_has_script_field,
    script_bashisms_without_bash_shebang,
    script_defines_functions,
    script_functions_mask_failures,
    script_has_bashism_in_posix_test,
    script_has_chmod_777,
    script_has_nested_backticks,
    script_has_shebang,
    script_has_unpinned_apt,
    script_has_unpinned_go_install,
    script_has_unpinned_npm,
    script_has_unquoted_command_substitution,
    script_has_unquoted_path_variables,
    script_has_unquoted_test_variables,
    script_has_unresolved_references,
    script_has_unsafe_array_expansion,
    script_has_unverified_git_clone,
    script_is_multiline,
    script_masks_failures,
    script_posix_shebang_with_bashisms,
    script_shebang_is_sh,
    script_uses_deprecated_ci_build_vars,
    script_uses_mktemp_when_needed,
)
from src.modules.gitlab_reference import (
    UnresolvedReference,
    construct_reference,
    resolve_reference_value,
)
from src.modules.job_composition import (
    EffectiveJobScripts,
    ScriptLine,
    _as_list,
    _flatten_script_items,
    _normalize_extends,
    _resolve_config_value,
    effective_scripts_as_values,
    script_lines_to_text,
)


def _entity(lines, **extra):
    values = {"effective_script": lines, "script": lines}
    values.update(extra)
    entity = {
        "name": "job",
        "source_file": "ci.yml",
        "line": 3,
        "values": values,
    }
    entity.update(values)
    return entity


def test_gitlab_reference_helpers():
    assert (
        str(UnresolvedReference(path=(".a", "script"))) == "!reference ['.a', 'script']"
    )
    node = SimpleNamespace(value=[".job", "script"])
    marker = construct_reference(None, node)
    assert marker.path == (".job", "script")
    scalar = construct_reference(None, SimpleNamespace(value="x"))
    assert scalar.path == ("x",)
    assert resolve_reference_value(
        UnresolvedReference(path=()), {}
    ) == UnresolvedReference(path=())
    assert resolve_reference_value(
        UnresolvedReference(path=("missing", "script")), {}
    ).path == ("missing", "script")
    registry = {".job": {"config": {"nested": {"k": 1}}}}
    assert (
        resolve_reference_value(
            UnresolvedReference(path=(".job", "nested", "k")), registry
        )
        == 1
    )
    assert isinstance(
        resolve_reference_value(
            UnresolvedReference(path=(".job", "nested", "missing")), registry
        ),
        UnresolvedReference,
    )


def test_job_composition_helpers():
    assert _as_list(None) == []
    assert _as_list("x") == ["x"]
    assert _normalize_extends(None) == []
    assert _normalize_extends("a") == ["a"]
    assert _normalize_extends(1) == ["1"]
    unresolved = []
    lines = _flatten_script_items(
        UnresolvedReference(path=(".x", "script")),
        source_file="f.yml",
        source_line=1,
        origin="direct",
        via="",
        unresolved=unresolved,
    )
    assert lines[0].origin == "unresolved_reference"
    assert unresolved
    lines = _flatten_script_items(
        [None],
        source_file="f.yml",
        source_line=1,
        origin="direct",
        via="",
        unresolved=unresolved,
    )
    assert lines[0].via.startswith("!reference")
    registry = {".job": {"config": {"script": ["echo"]}}}
    assert _resolve_config_value(
        UnresolvedReference(path=(".job", "script")), registry, []
    ) == ["echo"]
    assert _resolve_config_value({"a": [1]}, {}, []) == {"a": [1]}
    eff = EffectiveJobScripts(
        name="j",
        source_file="f",
        line=1,
        script=[ScriptLine(text="echo", source_file="f", source_line=1)],
    )
    values = effective_scripts_as_values(eff)
    assert values["script"] == ["echo"]
    assert script_lines_to_text([ScriptLine(text="a"), ScriptLine(text="")]) == ["a"]


def test_script_analysis_remaining_branches():
    assert job_has_script_field(_entity(["echo"]), "script")
    assert script_has_unquoted_path_variables(_entity(["cd $HOME"]))
    assert not script_has_unquoted_path_variables(_entity(['cd "$HOME"']))
    assert script_has_unquoted_command_substitution(_entity(["x=$(date)"]))
    assert not script_has_unquoted_command_substitution(_entity(['x="$(date)"']))
    assert script_has_unsafe_array_expansion(_entity(["echo ${arr[*]}"]))
    assert script_has_unsafe_array_expansion(_entity(["echo ${arr[@]}"]))
    assert not script_has_unsafe_array_expansion(_entity(['echo "${arr[@]}"']))
    assert script_has_nested_backticks(_entity(["x=`echo `date``"]))
    assert script_is_multiline(_entity(["a", "b"]))
    assert script_masks_failures(_entity(["cmd || true"]))
    assert script_defines_functions(_entity(["foo() {", "  echo", "}"]))
    assert script_functions_mask_failures(_entity(["foo() {", "  cmd || true", "}"]))
    assert script_has_unquoted_test_variables(_entity(["[ $FOO = bar ]"]))
    assert script_has_bashism_in_posix_test(_entity(["[ a == b ]"]))
    assert script_has_chmod_777(_entity(["chmod 777 file"]))
    assert script_has_unpinned_apt(_entity(["apt-get install curl"]))
    assert not script_has_unpinned_apt(_entity(["apt-get install curl=1"]))
    assert script_has_unpinned_npm(_entity(["npm install -g cowsay"]))
    assert not script_has_unpinned_npm(_entity(["npm install -g cowsay@1.0.0"]))
    assert script_has_unpinned_go_install(_entity(["go install example.com/cmd"]))
    assert not script_has_unpinned_go_install(
        _entity(["go install example.com/cmd@v1.2.3"])
    )
    assert script_has_unverified_git_clone(_entity(["git clone https://x.git"]))
    assert not script_has_unverified_git_clone(
        _entity(["git clone https://x.git", "git checkout abc123"])
    )
    assert script_uses_deprecated_ci_build_vars(_entity(["echo $CI_BUILD_ID"]))
    assert script_has_unresolved_references(
        _entity([], unresolved_script_references=["!reference [.x, script]"])
    )
    assert script_has_unresolved_references(
        _entity(
            [],
            script_provenance=[
                {"origin": "unresolved_reference", "text": "", "via": "x"}
            ],
        )
    )
    assert not script_has_unresolved_references(_entity(["echo"]))
    assert script_has_shebang(_entity(["#!/bin/bash", "echo"]))
    assert script_shebang_is_sh(_entity(["#!/bin/sh", "echo"]))
    assert script_bashisms_without_bash_shebang(_entity(["#!/bin/sh", "[[ -f x ]]"]))
    assert not script_bashisms_without_bash_shebang(_entity(["[[ -f x ]]"]))
    assert script_posix_shebang_with_bashisms(_entity(["#!/bin/sh", "[[ -f x ]]"]))
    assert script_uses_mktemp_when_needed(_entity(["tmp=$(mktemp)"]))
    msg = format_script_violation(
        {
            "name": "build",
            "source_file": "ci.yml",
            "line": 4,
            "values": {"extends_chain": [".base"]},
        },
        "boom",
    )
    assert "build" in msg and "extends:.base" in msg


class _Scenario:
    def __init__(self):
        self.skipped = False
        self.reason = None

    def skip(self, reason=None):
        self.skipped = True
        self.reason = reason


class _Ctx:
    def __init__(self):
        self.scenario_skipped = False
        self.stash = []
        self.step_mode = None
        self.compliance_entities = {"jobs": []}
        self.scenario = _Scenario()


def test_script_analysis_edge_branches():
    from src.compliance.script_analysis import (
        _script_lines,
        _strip_comment,
        script_defines_functions,
        script_downloads_without_checksum,
        script_functions_mask_failures,
        script_has_dangerous_rm,
        script_has_unpinned_pip,
        script_has_unquoted_variables,
        script_shebang_is_valid,
    )

    assert _script_lines({"values": {}}) == []
    assert _script_lines({"values": {"effective_script": [None, "echo"]}}) == ["echo"]
    assert _script_lines({"values": {"effective_script": "echo hi"}}) == ["echo hi"]
    assert _strip_comment('echo "a # b" # c') == 'echo "a # b"'
    # Quoted variable should not count as unquoted.
    assert not script_has_unquoted_variables(_entity(['echo "$FOO"']))
    assert not script_defines_functions(_entity(["echo hi"]))
    assert not script_functions_mask_failures(_entity(["echo hi"]))
    assert script_has_dangerous_rm(_entity(["rm -rf $DIR"]))
    assert not script_has_unpinned_pip(_entity(["pip install -r requirements.txt"]))
    assert script_shebang_is_valid(_entity(["echo no-shebang"]))
    assert not script_downloads_without_checksum(
        _entity(["curl https://x | bash"])
    )  # remote pipe excluded from checksum rule


def test_job_composition_missing_and_unresolved():
    from src.modules.gitlab_reference import UnresolvedReference
    from src.modules.job_composition import _walk_extends, compose_job_scripts

    assert _walk_extends("missing", {}) == []
    registry = {
        "job": {
            "config": {
                "script": [UnresolvedReference(path=(".missing", "script"))],
            },
            "source_file": "f.yml",
            "line": 1,
        },
        "child": {
            "config": {"extends": ["missing-parent"], "script": ["echo"]},
            "source_file": "f.yml",
            "line": 2,
        },
    }
    eff = compose_job_scripts("job", registry)
    assert eff.unresolved_references
    compose_job_scripts("child", registry)


def test_reference_with_real_loader():
    import yaml

    from src.modules.common import EnvLoader

    data = yaml.load("x: !reference [.job, script]\n", Loader=EnvLoader)
    assert isinstance(data["x"], UnresolvedReference)

    # Non-list constructed path through construct_object (scalar reference form)
    class FakeLoader:
        def construct_object(self, node):
            return "scalar"

        def construct_sequence(self, node):
            return ["a", "b"]

    marker = construct_reference(FakeLoader(), SimpleNamespace(value="not-a-list"))
    assert marker.path == ("scalar",)


def test_script_steps_helpers_and_assertions():
    ctx = _Ctx()
    steps._set_stash(ctx, [{"name": "j"}])
    assert ctx.stash[0]["name"] == "j"
    ctx.scenario_skipped = True
    steps._assert_none(ctx, lambda e: True, "x")
    steps._assert_all_true(ctx, lambda e: False, "x")
    steps._apply_filter(ctx, [], "reason")
    steps._set_stash_or_skip(ctx, [], skip_reason="empty")
    ctx.scenario_skipped = False
    ctx.stash = []
    try:
        steps._assert_none(ctx, lambda e: True, "x")
        assert False
    except AssertionError:
        pass
    try:
        steps._assert_all_true(ctx, lambda e: True, "x")
        assert False
    except AssertionError:
        pass
    ctx.stash = [_entity(["echo $FOO"])]
    try:
        steps._assert_none(ctx, lambda e: True, "bad")
        assert False
    except AssertionError as exc:
        assert "bad" in str(exc)
    ctx.stash = [_entity(["echo hi"])]
    steps._assert_all_true(ctx, lambda e: True, "ok")
    try:
        steps.then_packages_pinned(ctx, "unknown")
        assert False
    except AssertionError:
        pass
    ctx.compliance_entities = {
        "jobs": [
            {
                "name": "j",
                "values": {
                    "effective_script": ["echo hi"],
                    "script": ["echo hi"],
                    "before_script": ["echo before"],
                },
            }
        ]
    }
    steps.given_any_job_with_effective_script(ctx)
    steps.given_any_job_with_script(ctx)
    steps.given_any_job_with_before_script(ctx)
    ctx.stash = [_entity(["cd $HOME"])]
    steps.when_variables_in_path(ctx)
    ctx.stash = [_entity(["echo ${arr[*]}"])]
    steps.when_array_expanded(ctx)
    ctx.stash = [_entity(["echo hi"])]
    steps.when_array_expanded(ctx)
    ctx.stash = [_entity(["echo hi"])]
    steps.when_variables_in_path(ctx)
    ctx.stash = [_entity(["echo hi"], name=".hidden")]
    ctx.stash[0]["name"] = ".hidden"
    steps.when_name_starts_with_prefix(ctx, ".")
    ctx.stash = [_entity(["foo() {", "cmd || true", "}"])]
    try:
        steps.then_functions_propagate(ctx)
        assert False
    except AssertionError:
        pass
    ctx.stash = [_entity(["echo hi"])]
    steps.then_functions_propagate(ctx)
    # Cover continue path for quoted expansions and functions without masking.
    from src.compliance.script_analysis import script_defines_functions as _defines
    from src.compliance.script_analysis import script_functions_mask_failures as _masks
    from src.compliance.script_analysis import (
        script_has_unquoted_test_variables as _test_unquoted,
    )
    from src.compliance.script_analysis import (
        script_has_unquoted_variables as _unquoted,
    )

    assert not _unquoted(_entity(['echo "pre $FOO post"']))
    assert _defines(_entity(["foo() {", "echo ok", "}"]))
    assert not _masks(_entity(["foo() {", "echo ok", "}"]))
    assert not _test_unquoted(_entity(["echo hi"]))
    # when_command_substitution / when_array else branches
    ctx.stash = [_entity(["echo hi"])]
    steps.when_command_substitution(ctx)
    steps.when_array_expanded(ctx)


def test_all_script_then_steps_smoke():
    """Exercise every Then/When step with a safe or failing stash."""
    good = _entity(
        [
            "set -euo pipefail",
            'echo "$FOO"',
            'cd "$HOME"',
            'x="$(date)"',
            'echo "${arr[@]}"',
            "curl -fsSL https://example.com -o /tmp/f",
            "sha256sum -c sums",
            "apk add curl=1",
            "pip install r==1",
            "apt-get install curl=1",
            "npm install -g cowsay@1",
            "go install example.com/cmd@v1",
            "git clone https://x.git",
            "git checkout abc",
            "tmp=$(mktemp)",
            'if [ "$FOO" = bar ]; then echo x; fi',
            "#!/usr/bin/env bash",
        ]
    )
    ctx = _Ctx()
    ctx.stash = [good]
    steps.when_variable_expanded(ctx)
    steps.when_command_substitution(ctx)
    steps.when_multiline_script(ctx)
    steps.when_rm_recursive(ctx)
    steps.when_pipeline_used(ctx)
    steps.when_temp_files_required(ctx)
    steps.then_variables_quoted(ctx)
    steps.then_path_variables_quoted(ctx)
    steps.then_cmd_sub_quoted(ctx)
    steps.then_array_at_syntax(ctx)
    steps.then_strict_mode_table(ctx)
    steps.then_failure_handled(ctx)
    steps.then_file_paths_quoted(ctx)
    steps.then_mktemp_used(ctx)
    steps.then_rm_protected(ctx)
    steps.then_no_backticks(ctx)
    steps.then_nested_dollar(ctx)
    steps.then_posix_operators(ctx)
    steps.then_test_vars_quoted(ctx)
    steps.then_pipefail(ctx)
    steps.then_no_eval(ctx)
    steps.then_no_remote_pipe(ctx)
    steps.then_user_input_safe(ctx)
    steps.then_no_secrets(ctx)
    steps.then_downloads_checksum(ctx)
    for manager in ("apk", "pip", "apt", "npm", "go"):
        steps.then_packages_pinned(ctx, manager)
    steps.then_git_clone_verified(ctx)
    steps.then_curl_fail(ctx)
    steps.then_no_ci_build(ctx)
    steps.then_no_unresolved_refs(ctx)
    steps.then_shebang_valid(ctx)
    steps.then_bash_declared(ctx)
    steps.then_posix_no_bashisms(ctx)
    steps.then_no_chmod_777(ctx)
