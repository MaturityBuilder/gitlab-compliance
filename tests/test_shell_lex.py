"""Unit tests for POSIX/bash shell_lex quoting and expansion scanning."""

from __future__ import annotations

from src.compliance.script_analysis import (
    script_has_unquoted_command_substitution,
    script_has_unquoted_variables,
)
from src.compliance.shell_lex import (
    has_bash_double_bracket,
    has_bash_process_substitution,
    iter_command_substitutions,
    quote_state_at,
    strip_comment,
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


def test_nested_dollar_quote_context_hostname():
    line = 'check="$(curl "$HOSTNAME" | jq -r \'.message\')"'
    idx = line.index("$HOSTNAME")
    assert quote_state_at(line, idx) == "double"
    assert not script_has_unquoted_variables(_entity([line]))
    assert not script_has_unquoted_command_substitution(_entity([line]))


def test_unquoted_outer_cmdsub_still_fails():
    line = 'check=$(curl "$HOSTNAME")'
    assert script_has_unquoted_command_substitution(_entity([line]))
    assert not script_has_unquoted_variables(_entity([line]))


def test_nested_cmdsub_inside_quoted_outer():
    line = 'echo "$(echo $(date))"'
    assert not script_has_unquoted_command_substitution(_entity([line]))
    spans = list(iter_command_substitutions(line, nested=True))
    assert len(spans) >= 2
    top = list(iter_command_substitutions(line, nested=False))
    assert len(top) == 1
    assert quote_state_at(line, top[0].start) == "double"


def test_quote_adjacent_still_unquoted():
    assert script_has_unquoted_variables(_entity(['echo "$PREFIX"$SUFFIX']))


def test_parameter_default_quoted():
    line = 'echo "${foo:-default}"'
    assert not script_has_unquoted_variables(_entity([line]))


def test_bash_greeting_cmdsub_quoting():
    assert script_has_unquoted_command_substitution(
        _entity(['greeting=$(greet "Hello")'])
    )
    assert not script_has_unquoted_command_substitution(
        _entity(['greeting="$(greet "Hello")"'])
    )


def test_process_substitution_detected():
    line = "cat <(echo hi)"
    assert has_bash_process_substitution(line)
    spans = list(iter_command_substitutions(line))
    assert any(line[s.start] == "<" for s in spans)
    # Process subst must not fail QUOTE-003 (unquoted command substitution).
    assert not script_has_unquoted_command_substitution(_entity([line]))
    assert not script_has_unquoted_command_substitution(
        _entity(["diff <(sort a) <(sort b)"])
    )
    assert not script_has_unquoted_command_substitution(_entity(["cmd >(tee log)"]))


def test_positional_params_not_unquoted_variables():
    assert not script_has_unquoted_variables(_entity(["echo $1"]))
    assert not script_has_unquoted_variables(_entity(["echo $2 $@ $* $# $? $$ $!"]))
    assert not script_has_unquoted_variables(_entity(["echo ${1}"]))
    # Named vars still fail when unquoted.
    assert script_has_unquoted_variables(_entity(["echo $NAME"]))


def test_double_bracket_helper():
    assert has_bash_double_bracket("if [[ $USER = 'x' ]]; then")


def test_strip_comment_ignores_hash_inside_cmdsub():
    line = 'echo "$(echo # not a comment)" # real'
    assert strip_comment(line) == 'echo "$(echo # not a comment)"'


def test_positional_digit_params_consumed():
    """``$1``–``$9`` must be consumed as one token (not ``nxt in \"0-9\"``)."""
    from src.compliance.shell_lex import _consume_dollar_construct, _Frame

    for digit in "0123456789":
        line = f"echo ${digit}x"
        end = _consume_dollar_construct(line, line.index("$"), _Frame(), "bash")
        assert end == line.index("$") + 2, digit
        assert quote_state_at(line, line.index("$")) == "none"


def test_quote_state_at_dollar_inside_double_quotes():
    line = 'echo "$VAR"'
    dollar = line.index("$")
    # Exact hit on `$` uses the early ``i == index`` frame return (double).
    assert quote_state_at(line, dollar) == "double"
    assert quote_state_at(line, line.index('"')) == "none"


def test_arithmetic_vs_command_substitution_spans():
    arith = "x=$((1 + 2))"
    cmd_spans = list(iter_command_substitutions(arith, nested=False))
    assert cmd_spans == []

    nested_arith_in_cmd = 'echo "$(echo $((1+1)))"'
    top = list(iter_command_substitutions(nested_arith_in_cmd, nested=False))
    assert len(top) == 1
    assert quote_state_at(nested_arith_in_cmd, top[0].start) == "double"


def test_ansi_c_and_locale_quoted_strings():
    ansi = "echo $'line\\n'"
    assert quote_state_at(ansi, ansi.index("$")) == "none"
    # No parameter expansion inside $'...'
    assert not script_has_unquoted_variables(_entity([ansi]))

    locale = 'echo $"hello"'
    assert not script_has_unquoted_variables(_entity([locale]))


def test_nested_parameter_default_in_braces():
    line = 'echo "${outer:-${inner:-fallback}}"'
    assert not script_has_unquoted_variables(_entity([line]))
    line_bad = "echo ${outer:-${inner}}"
    assert script_has_unquoted_variables(_entity([line_bad]))


def test_escaped_dollar_and_hash_in_cmdsub_in_fixtures_style():
    assert not script_has_unquoted_variables(_entity([r"echo \$LITERAL"]))
    assert not script_has_unquoted_variables(
        _entity(['echo "${APP_NAME:-shell-demo}"'])
    )
    line = 'echo "$(echo foo # not outer)" # real'
    assert strip_comment(line) == 'echo "$(echo foo # not outer)"'
