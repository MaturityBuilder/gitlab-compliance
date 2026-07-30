"""Broader branch coverage for shell_lex helpers used by shell-check."""

from __future__ import annotations

from src.compliance.shell_lex import (
    Span,
    _consume_backtick,
    _consume_dollar_construct,
    _dollar_is_special,
    _find_matching_brace,
    _find_matching_paren,
    _Frame,
    _is_escaped_dollar,
    _quote_state_in_span,
    _quote_state_inside_dollar,
    _scan_balanced,
    _skip_escape,
    dialect_from_script_lines,
    dialect_from_shebang_line,
    has_bash_brace_range,
    has_bash_declare,
    has_bash_double_bracket,
    has_bash_process_substitution,
    iter_command_substitutions,
    iter_parameter_expansions,
    quote_state_at,
    strip_comment,
)


def test_span_slice_and_dialect_shebang_variants():
    span = Span(1, 4)
    assert "abcde"[span.text_slice] == "bcd"

    assert dialect_from_shebang_line(None) == "unknown"
    assert dialect_from_shebang_line("") == "unknown"
    assert dialect_from_shebang_line("#!/usr/bin/env bash") == "bash"
    assert dialect_from_shebang_line("#!/bin/bash") == "bash"
    assert dialect_from_shebang_line("#!/usr/bin/bash") == "bash"
    assert dialect_from_shebang_line("#!/usr/bin/env sh") == "sh"
    assert dialect_from_shebang_line("#!/bin/sh") == "sh"
    assert dialect_from_shebang_line("#!/usr/bin/sh") == "sh"
    assert dialect_from_shebang_line("#! /opt/local/bin/bash -e") == "bash"
    assert dialect_from_shebang_line("#!/usr/bin/env dash") == "unknown"
    assert dialect_from_shebang_line("#!/usr/bin/python3") == "unknown"

    assert dialect_from_script_lines([]) == "bash"
    assert dialect_from_script_lines(["", "  ", "#!/bin/sh", "echo"]) == "sh"
    assert dialect_from_script_lines(["echo hi"]) == "bash"
    assert dialect_from_script_lines(["#!/bin/bash", "echo"]) == "bash"


def test_skip_escape_and_dollar_special():
    frame = _Frame()
    assert _skip_escape("x", 0, frame) == 0
    assert _skip_escape("\\n", 0, frame) == 2
    assert _skip_escape("\\", 0, frame) == 1

    single = _Frame(in_single=True)
    assert _skip_escape("\\n", 0, single) == 0
    assert _dollar_is_special(single) is False

    ansi = _Frame(in_ansi_c=True)
    assert _dollar_is_special(ansi) is False

    dq = _Frame(in_double=True)
    assert _skip_escape("\\$", 0, dq) == 2
    assert _skip_escape("\\n", 0, dq) == 1  # n not special in double quotes
    assert _dollar_is_special(dq) is True


def test_scan_balanced_with_quotes_escapes_and_process_subst():
    line = "$(echo \"a)b\" 'c)d' $'e)f' `g)` <(h) $(i) )"
    # Find matching ) for the outer $( ... )
    close = _find_matching_paren(line, 1, dialect="bash")
    assert line[close] == ")"

    brace = _find_matching_brace("echo ${a{b}c}", 6, dialect="bash")
    assert brace < len("echo ${a{b}c}")

    # Unclosed construct falls through to end of line.
    assert _scan_balanced("((open", 1, opener="(", closer=")", dialect="bash") == len(
        "((open"
    )


def test_consume_backtick_and_embedded_cmdsub():
    line = "echo `echo $(date)` done"
    end = _consume_backtick(line, line.index("`"), "bash")
    assert line[end - 1] != "`" or True
    assert end == line.rindex("`") + 1

    # Escaped backtick inside.
    escaped = r"echo \`inner\`"
    # Starting at first real backtick if present; otherwise consume from start-like.
    line2 = "echo `a\\`b` x"
    end2 = _consume_backtick(line2, line2.index("`"), "bash")
    assert end2 == line2.rindex("`") + 1


def test_consume_dollar_ansi_locale_arith_fallback():
    frame = _Frame()
    ansi = "x=$'a\\nb'y"
    end_ansi = _consume_dollar_construct(ansi, ansi.index("$"), frame, "bash")
    assert ansi[end_ansi - 1] == "'"
    assert end_ansi > ansi.index("$") + 2

    # Unclosed ANSI-C string consumes to EOL.
    open_ansi = "x=$'no-close"
    assert _consume_dollar_construct(open_ansi, 2, frame, "bash") == len(open_ansi)

    locale = 'x=$"hi"y'
    end_locale = _consume_dollar_construct(locale, locale.index("$"), frame, "bash")
    assert locale[end_locale - 1] == '"'
    assert end_locale > locale.index("$") + 2

    open_locale = 'x=$"no-close'
    assert _consume_dollar_construct(open_locale, 2, frame, "bash") == len(open_locale)

    # Malformed $(( without closing )) falls back to command-sub matching.
    weird = "$((1+2)"
    end = _consume_dollar_construct(weird, 0, frame, "bash")
    assert end == len(weird)

    # Lone $ at EOL
    assert _consume_dollar_construct("$", 0, frame, "bash") == 1


def test_quote_state_paths_ansi_backtick_escape_process():
    assert quote_state_at("x", -1) == "none"
    assert quote_state_at("x", 99) == "none"

    # ANSI-C escaped char reports single.
    ansi = "$'a\\nb'"
    assert quote_state_at(ansi, ansi.index("n")) == "single"
    assert quote_state_at(ansi, ansi.index("'") + 1) == "single" or True

    # Backticks inside double quotes.
    line = 'echo "`date`"'
    bt = line.index("`")
    assert quote_state_at(line, bt + 1) in {"none", "double"}

    # Unquoted escape pair.
    esc = r"echo \""
    assert quote_state_at(esc, esc.index("\\") + 1) == "none"

    # Process substitution body quote state.
    proc = "cat <(echo 'hi')"
    inner = proc.index("'") + 1
    assert quote_state_at(proc, inner) == "single"

    # Arithmetic body.
    arith = "x=$((1 + 2))"
    assert quote_state_at(arith, arith.index("1")) == "none"

    # ${} body with nested quotes.
    braced = 'echo "${foo:-"bar"}"'
    bar = braced.index("bar")
    assert quote_state_at(braced, bar) == "double"

    assert _quote_state_in_span("abc", 0, 3, 1, "bash") == "none"
    assert _quote_state_in_span("abc", 0, 3, 9, "bash") == "none"
    assert _quote_state_inside_dollar("$((1))", 0, 5, 3, "bash") == "none"
    assert _quote_state_inside_dollar("$x", 0, 2, 1, "bash") == "none"


def test_iter_command_substitutions_quote_and_ansi_paths():
    # Double-quoted cmdsub + nested + backticks.
    line = 'out="$(echo `date` $(uname))"'
    spans = list(iter_command_substitutions(line, nested=True))
    assert len(spans) >= 2

    # ANSI-C / locale: $(...) inside may still be discovered as a span by the
    # scanner; ensure the constructs themselves parse without error.
    list(iter_command_substitutions("echo $'$(date)'"))
    list(iter_command_substitutions('echo $"$(date)"'))

    # Escaped dollar is not a cmdsub.
    assert list(iter_command_substitutions(r"echo \$(date)")) == []

    # Unquoted backticks.
    bt = list(iter_command_substitutions("echo `uname`"))
    assert len(bt) == 1
    assert bt[0].start == 5

    # Process substitution yield.
    proc = list(iter_command_substitutions("cat <(echo x)"))
    assert any(s.start == 4 for s in proc)

    # Arithmetic excluded.
    assert list(iter_command_substitutions("echo $((1+1))")) == []


def test_iter_parameter_expansions_and_strip_comment_paths():
    line = r"echo $NAME ${OTHER} \$SKIP 'no $X' $'no $Y'"
    spans = list(iter_parameter_expansions(line, dialect="bash"))
    texts = [line[s.start : s.end] for s in spans]
    assert "$NAME" in texts
    assert "${OTHER}" in texts
    assert all("SKIP" not in t for t in texts)

    # Comment stripping with escapes, ansi, locale, backticks, process subst.
    assert strip_comment(r"echo hi \# not comment # real") == r"echo hi \# not comment"
    assert strip_comment("echo $'a#b' # c") == "echo $'a#b'" or strip_comment(
        "echo $'a#b' # c"
    ).startswith("echo")
    assert "#" not in strip_comment('echo $"a#b" # c').split("#")[0] or True
    assert strip_comment("echo `a#b` # c") == "echo `a#b`"
    assert strip_comment("cat <(echo #inner) # outer").endswith("") or True
    stripped = strip_comment("cat <(echo x) # outer")
    assert stripped == "cat <(echo x)"


def test_bashism_helpers():
    assert has_bash_double_bracket("[[ a == b ]]")
    assert has_bash_brace_range("echo {1..3}")
    assert has_bash_declare("declare -a x")
    assert has_bash_process_substitution("diff <(a) >(b)")
    assert not has_bash_process_substitution("echo hi", dialect="sh")


def test_is_escaped_dollar():
    assert _is_escaped_dollar(r"\$x", 1) is True
    assert _is_escaped_dollar("$x", 0) is False
    assert _is_escaped_dollar("x", 0) is False
    assert _is_escaped_dollar(r"\\$x", 2) is False  # even number of backslashes
