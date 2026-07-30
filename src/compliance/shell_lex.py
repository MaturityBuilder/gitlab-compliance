"""POSIX- and bash-aware quoting / expansion scanning for shell-check.

Implements the nested quote rules from POSIX Issue 7 Shell Command Language
§2.2–2.3 and §2.6, plus bash extensions commonly used in CI scripts
(parameter defaults, process substitution, ``$'...'`` / ``$"..."``, ``[[``).

Key POSIX rule (§2.2.3): characters between ``$(`` and the matching ``)`` are
not affected by enclosing double quotes — tokenizing is applied recursively.
That makes ``check="$(curl "$HOSTNAME")"`` correctly treat ``$HOSTNAME`` as
double-quoted inside the nested command body.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Literal

Dialect = Literal["bash", "sh", "unknown"]
QuoteState = Literal["none", "single", "double"]

_SHEBANG_BASH = re.compile(r"^#!\s*(?:/usr/bin/env\s+bash|/bin/bash|/usr/bin/bash)\b")
_SHEBANG_SH = re.compile(r"^#!\s*(?:/usr/bin/env\s+sh|/bin/sh|/usr/bin/sh)\b")
_PARAM_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_BRACE_RANGE = re.compile(r"\{-?\d+\.\.-?\d+(?:\.\.-?\d+)?\}")


@dataclass(frozen=True)
class Span:
    """Half-open character span ``[start, end)`` on a script line."""

    start: int
    end: int

    @property
    def text_slice(self) -> slice:
        return slice(self.start, self.end)


@dataclass
class _Frame:
    in_single: bool = False
    in_double: bool = False
    # Bash ANSI-C / locale quoted strings.
    in_ansi_c: bool = False
    in_locale_dq: bool = False


def dialect_from_shebang_line(line: str | None) -> Dialect:
    """Return dialect inferred from a shebang line (or unknown)."""
    if not line or not line.startswith("#!"):
        return "unknown"
    if _SHEBANG_BASH.match(line):
        return "bash"
    if _SHEBANG_SH.match(line):
        return "sh"
    if "bash" in line:
        return "bash"
    if re.search(r"\bsh\b", line):
        return "sh"
    return "unknown"


def dialect_from_script_lines(lines: list[str]) -> Dialect:
    """Infer dialect from script lines; CI scripts without shebang default to bash."""
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#!"):
            return dialect_from_shebang_line(stripped)
        break
    # GitLab job scripts typically run under bash when no shebang is present.
    return "bash"


def _frame_state(frame: _Frame) -> QuoteState:
    if frame.in_single or frame.in_ansi_c:
        return "single"
    if frame.in_double or frame.in_locale_dq:
        return "double"
    return "none"


def _dollar_is_special(frame: _Frame) -> bool:
    """Whether ``$`` introduces an expansion in the current quote context."""
    if frame.in_single or frame.in_ansi_c:
        return False
    return True


def _skip_escape(line: str, index: int, frame: _Frame) -> int:
    """Advance past a backslash escape; return new index after the escape pair."""
    if index >= len(line) or line[index] != "\\":
        return index
    if frame.in_single:
        return index
    if frame.in_double or frame.in_locale_dq:
        # POSIX: \\ only special before $ ` " \\ <newline>
        if index + 1 < len(line) and line[index + 1] in '$`"\\\n':
            return index + 2
        return index + 1
    # Unquoted: backslash escapes next char (except newline continuation).
    if index + 1 < len(line):
        return index + 2
    return index + 1


def _find_matching_paren(line: str, open_index: int, *, dialect: Dialect) -> int:
    """Return index of matching ``)`` for ``(`` at ``open_index``, or ``len(line)``."""
    return _scan_balanced(line, open_index + 1, opener="(", closer=")", dialect=dialect)


def _find_matching_brace(line: str, open_index: int, *, dialect: Dialect) -> int:
    """Return index of matching ``}`` for ``{`` at ``open_index``, or ``len(line)``."""
    return _scan_balanced(line, open_index + 1, opener="{", closer="}", dialect=dialect)


def _scan_balanced(
    line: str,
    start: int,
    *,
    opener: str,
    closer: str,
    dialect: Dialect,
) -> int:
    """Scan from ``start`` until nesting depth for opener/closer returns to 0."""
    frame = _Frame()
    depth = 1
    i = start
    while i < len(line):
        if frame.in_single:
            if line[i] == "'":
                frame.in_single = False
            i += 1
            continue
        if frame.in_ansi_c:
            if line[i] == "\\" and i + 1 < len(line):
                i += 2
                continue
            if line[i] == "'":
                frame.in_ansi_c = False
            i += 1
            continue
        if frame.in_double or frame.in_locale_dq:
            if line[i] == "\\":
                i = _skip_escape(line, i, frame)
                continue
            if line[i] == '"':
                frame.in_double = False
                frame.in_locale_dq = False
                i += 1
                continue
            if line[i] == "$" and _dollar_is_special(frame):
                i = _consume_dollar_construct(line, i, frame, dialect)
                continue
            if line[i] == "`":
                i = _consume_backtick(line, i, dialect)
                continue
            i += 1
            continue

        # Unquoted body of nested construct.
        if line[i] == "\\":
            i = _skip_escape(line, i, frame)
            continue
        if line[i] == "'":
            if dialect == "bash" and i > 0 and line[i - 1] == "$":
                # Handled via $' — should not reach here for $'
                pass  # pragma: no cover
            frame.in_single = True
            i += 1
            continue
        if line[i] == '"':
            frame.in_double = True
            i += 1
            continue
        if line[i] == "`":
            i = _consume_backtick(line, i, dialect)
            continue
        if line[i] == "$" and _dollar_is_special(frame):
            i = _consume_dollar_construct(line, i, frame, dialect)
            continue
        if (
            dialect == "bash"
            and line[i] in "<>"
            and i + 1 < len(line)
            and line[i + 1] == "("
        ):
            close = _find_matching_paren(line, i + 1, dialect=dialect)
            i = min(close + 1, len(line))
            continue
        if line[i] == opener:
            depth += 1
            i += 1
            continue
        if line[i] == closer:
            depth -= 1
            if depth == 0:
                return i
            i += 1
            continue
        i += 1
    return len(line)


def _consume_backtick(line: str, start: int, dialect: Dialect) -> int:
    """Return index after closing backtick starting at ``start``."""
    i = start + 1
    while i < len(line):
        if line[i] == "\\" and i + 1 < len(line) and line[i + 1] in "$`\\":
            i += 2
            continue
        if line[i] == "`":
            return i + 1
        if line[i] == "$" and i + 1 < len(line) and line[i + 1] == "(":
            # Embedded $() inside backticks.
            close = _find_matching_paren(line, i + 1, dialect=dialect)
            i = min(close + 1, len(line))
            continue
        i += 1
    return len(line)


def _consume_dollar_construct(
    line: str, start: int, frame: _Frame, dialect: Dialect
) -> int:
    """Consume ``$...`` starting at ``start``; return index after the construct."""
    if start >= len(line) or line[start] != "$":
        return start + 1
    if start + 1 >= len(line):
        return start + 1

    nxt = line[start + 1]

    # Bash $'...' / $"..."
    if dialect == "bash" and nxt == "'" and not frame.in_double:
        i = start + 2
        while i < len(line):
            if line[i] == "\\" and i + 1 < len(line):
                i += 2
                continue
            if line[i] == "'":
                return i + 1
            i += 1
        return len(line)
    if dialect == "bash" and nxt == '"' and not frame.in_double:
        # $"..." — treat like double quotes for content.
        i = start + 2
        nested = _Frame(in_locale_dq=True)
        while i < len(line):
            if i < len(line) and line[i] == "\\":
                i = _skip_escape(line, i, nested)
                continue
            if line[i] == '"':
                return i + 1
            if line[i] == "$":
                i = _consume_dollar_construct(line, i, nested, dialect)
                continue
            i += 1
        return len(line)

    if nxt == "(":
        # $(( arith )) vs $( command )
        if start + 2 < len(line) and line[start + 2] == "(":
            close = _scan_balanced(
                line, start + 3, opener="(", closer=")", dialect=dialect
            )
            # Expect ))
            if close < len(line) and close + 1 < len(line) and line[close + 1] == ")":
                return close + 2
            # Fallback: treat as command sub starting at first (
            close = _find_matching_paren(line, start + 1, dialect=dialect)
            return min(close + 1, len(line))
        close = _find_matching_paren(line, start + 1, dialect=dialect)
        return min(close + 1, len(line))

    if nxt == "{":
        close = _find_matching_brace(line, start + 1, dialect=dialect)
        return min(close + 1, len(line))

    # Positional ($1) and special ($@ $* $? …) parameters — one character.
    # Note: ``"0-9"`` is NOT a digit range in Python (only chars 0, -, 9).
    if nxt.isdigit() or nxt in "@*#?-!$":
        return start + 2
    match = _PARAM_NAME.match(line, start + 1)
    if match:
        return match.end()
    return start + 1


def quote_state_at(line: str, index: int, *, dialect: Dialect = "bash") -> QuoteState:
    """Return effective quote state at ``index`` with nested ``$()`` contexts.

    Characters inside ``$(...)`` use an independent quote context (POSIX §2.2.3),
    so ``"$HOSTNAME"`` inside ``"$(curl "$HOSTNAME")"`` is double-quoted.
    """
    if index < 0 or index >= len(line):
        return "none"

    frame = _Frame()
    i = 0
    while i < len(line):
        # Exact cursor hit — return current frame. Later branches must not
        # re-test ``i == index`` (unreachable once this guard runs).
        if i == index:
            return _frame_state(frame)

        # Single-quoted region
        if frame.in_single:
            if line[i] == "'":
                frame.in_single = False
            i += 1
            continue

        if frame.in_ansi_c:
            if line[i] == "\\" and i + 1 < len(line):
                if i + 1 == index:
                    return "single"
                i += 2
                continue
            if line[i] == "'":
                frame.in_single = False
                frame.in_ansi_c = False
            i += 1
            continue

        # Double-quoted / locale double-quoted
        if frame.in_double or frame.in_locale_dq:
            if line[i] == "\\":
                nxt = _skip_escape(line, i, frame)
                if i < index < nxt:
                    return "double"
                i = nxt
                continue
            if line[i] == '"':
                frame.in_double = False
                frame.in_locale_dq = False
                i += 1
                continue
            if line[i] == "$" and _dollar_is_special(frame):
                # Enter nested constructs with independent quoting for bodies.
                end = _consume_dollar_construct(line, i, frame, dialect)
                if i < index < end:
                    return _quote_state_inside_dollar(line, i, end, index, dialect)
                i = end
                continue
            if line[i] == "`":
                end = _consume_backtick(line, i, dialect)
                if i < index < end:
                    return _quote_state_in_span(line, i + 1, end - 1, index, dialect)
                i = end
                continue
            i += 1
            continue

        # Unquoted
        if line[i] == "\\":
            nxt = _skip_escape(line, i, frame)
            if i < index < nxt:
                return "none"
            i = nxt
            continue
        if (
            dialect == "bash"
            and line[i] == "$"
            and i + 1 < len(line)
            and line[i + 1] == "'"
        ):
            frame.in_ansi_c = True
            i += 2
            continue
        if (
            dialect == "bash"
            and line[i] == "$"
            and i + 1 < len(line)
            and line[i + 1] == '"'
        ):
            frame.in_locale_dq = True
            i += 2
            continue
        if line[i] == "'":
            frame.in_single = True
            i += 1
            continue
        if line[i] == '"':
            frame.in_double = True
            i += 1
            continue
        if line[i] == "`":
            end = _consume_backtick(line, i, dialect)
            if i < index < end:
                return _quote_state_in_span(line, i + 1, end - 1, index, dialect)
            i = end
            continue
        if line[i] == "$" and _dollar_is_special(frame):
            end = _consume_dollar_construct(line, i, frame, dialect)
            if i < index < end:
                return _quote_state_inside_dollar(line, i, end, index, dialect)
            i = end
            continue
        if (
            dialect == "bash"
            and line[i] in "<>"
            and i + 1 < len(line)
            and line[i + 1] == "("
        ):
            close = _find_matching_paren(line, i + 1, dialect=dialect)
            end = min(close + 1, len(line))
            if i < index < end:
                return _quote_state_in_span(line, i + 2, close, index, dialect)
            i = end
            continue
        i += 1

    return "none"  # pragma: no cover — in-range indexes always hit i == index


def _quote_state_inside_dollar(
    line: str, dollar_start: int, dollar_end: int, index: int, dialect: Dialect
) -> QuoteState:
    """Quote state for ``index`` inside a ``$...`` construct starting at ``dollar_start``."""
    if dollar_start + 1 >= dollar_end:
        return "none"
    kind = line[dollar_start + 1]
    if kind == "(":
        # Skip $(( or $(
        body_start = dollar_start + 2
        if body_start < dollar_end and line[dollar_start + 2] == "(":
            # arithmetic $(( ... ))
            body_start = dollar_start + 3
            body_end = dollar_end - 2 if dollar_end >= 2 else dollar_end
        else:
            body_end = dollar_end - 1  # exclude closing )
        if body_start <= index < body_end:
            return _quote_state_in_span(line, body_start, body_end, index, dialect)
        return "none"
    if kind == "{":
        # ${...} — expansions inside braces still use nested scan for embedded quotes/subs
        body_start = dollar_start + 2
        body_end = dollar_end - 1
        if body_start <= index < body_end:
            return _quote_state_in_span(line, body_start, body_end, index, dialect)
        return "none"
    # $NAME — no inner body
    return "none"


def _quote_state_in_span(
    line: str, start: int, end: int, index: int, dialect: Dialect
) -> QuoteState:
    """Evaluate quote state at absolute ``index`` within ``line[start:end]``."""
    if index < start or index >= end:
        return "none"
    # Recurse by scanning only the span via a relative view.
    relative = index - start
    return quote_state_at(line[start:end], relative, dialect=dialect)


def _is_escaped_dollar(line: str, index: int) -> bool:
    """Return True when ``line[index]`` is a ``$`` escaped by an odd backslash run."""
    if index >= len(line) or line[index] != "$":
        return False
    count = 0
    j = index - 1
    while j >= 0 and line[j] == "\\":
        count += 1
        j -= 1
    return count % 2 == 1


def iter_command_substitutions(
    line: str, *, dialect: Dialect = "bash", nested: bool = True
) -> Iterator[Span]:
    """Yield spans of ``$(...)``, backticks, and bash process substitutions.

    When ``nested`` is False, only top-level substitutions are yielded (not those
    inside another ``$()`` / backtick body). Use that for word-splitting policies.
    """
    yield from _iter_command_substitutions_impl(
        line, dialect=dialect, nested=nested, absolute_offset=0
    )


def _iter_command_substitutions_impl(
    line: str,
    *,
    dialect: Dialect,
    nested: bool,
    absolute_offset: int,
) -> Iterator[Span]:
    i = 0
    frame = _Frame()
    while i < len(line):
        if frame.in_single:
            if line[i] == "'":
                frame.in_single = False
            i += 1
            continue
        if frame.in_ansi_c:
            if line[i] == "\\" and i + 1 < len(line):
                i += 2
                continue
            if line[i] == "'":
                frame.in_ansi_c = False
            i += 1
            continue
        if frame.in_double or frame.in_locale_dq:
            if line[i] == "\\":
                i = _skip_escape(line, i, frame)
                continue
            if line[i] == '"':
                frame.in_double = False
                frame.in_locale_dq = False
                i += 1
                continue
            if (
                line[i] == "$"
                and _dollar_is_special(frame)
                and not _is_escaped_dollar(line, i)
            ):
                start = i
                end = _consume_dollar_construct(line, i, frame, dialect)
                is_arith = i + 2 < len(line) and line[i + 1 : i + 3] == "(("
                is_cmd = i + 1 < len(line) and line[i + 1] == "(" and not is_arith
                if is_cmd:
                    yield Span(start + absolute_offset, end + absolute_offset)
                    if nested:
                        yield from _nested_cmdsubs_in_dollar(
                            line, start, end, dialect, absolute_offset
                        )
                i = end
                continue
            if line[i] == "`":
                end = _consume_backtick(line, i, dialect)
                yield Span(i + absolute_offset, end + absolute_offset)
                i = end
                continue
            i += 1
            continue

        if line[i] == "\\":
            i = _skip_escape(line, i, frame)
            continue
        if (
            dialect == "bash"
            and line[i] == "$"
            and i + 1 < len(line)
            and line[i + 1] == "'"
        ):
            frame.in_ansi_c = True
            i += 2
            continue
        if (
            dialect == "bash"
            and line[i] == "$"
            and i + 1 < len(line)
            and line[i + 1] == '"'
        ):
            frame.in_locale_dq = True
            i += 2
            continue
        if line[i] == "'":
            frame.in_single = True
            i += 1
            continue
        if line[i] == '"':
            frame.in_double = True
            i += 1
            continue
        if line[i] == "`":
            end = _consume_backtick(line, i, dialect)
            yield Span(i + absolute_offset, end + absolute_offset)
            i = end
            continue
        if (
            line[i] == "$"
            and i + 1 < len(line)
            and line[i + 1] == "("
            and not _is_escaped_dollar(line, i)
        ):
            start = i
            end = _consume_dollar_construct(line, i, frame, dialect)
            is_arith = i + 2 < len(line) and line[i + 2] == "("
            if not is_arith:
                yield Span(start + absolute_offset, end + absolute_offset)
                if nested:
                    yield from _nested_cmdsubs_in_dollar(
                        line, start, end, dialect, absolute_offset
                    )
            i = end
            continue
        if line[i] == "$":
            i = _consume_dollar_construct(line, i, frame, dialect)
            continue
        if (
            dialect == "bash"
            and line[i] in "<>"
            and i + 1 < len(line)
            and line[i + 1] == "("
        ):
            close = _find_matching_paren(line, i + 1, dialect=dialect)
            end = min(close + 1, len(line))
            yield Span(i + absolute_offset, end + absolute_offset)
            i = end
            continue
        i += 1


def _nested_cmdsubs_in_dollar(
    line: str,
    start: int,
    end: int,
    dialect: Dialect,
    absolute_offset: int = 0,
) -> Iterator[Span]:
    if start + 2 >= end:
        return
    if line[start + 1] != "(":
        return
    if start + 2 < len(line) and line[start + 2] == "(":
        return  # arithmetic
    body_start = start + 2
    body_end = end - 1
    if body_start >= body_end:
        return
    yield from _iter_command_substitutions_impl(
        line[body_start:body_end],
        dialect=dialect,
        nested=True,
        absolute_offset=absolute_offset + body_start,
    )


def iter_parameter_expansions(
    line: str, *, dialect: Dialect = "bash"
) -> Iterator[Span]:
    """Yield ``$NAME`` / ``${...}`` spans that are real expansions (not in single quotes)."""
    i = 0
    while i < len(line):
        if line[i] != "$":
            i += 1
            continue
        if _is_escaped_dollar(line, i):
            i += 1
            continue
        state = quote_state_at(line, i, dialect=dialect)
        if state == "single":
            i += 1
            continue
        # Skip command substitutions / arith / process — those are not params.
        if i + 1 < len(line) and line[i + 1] == "(":
            i = _consume_dollar_construct(line, i, _Frame(), dialect)
            continue
        if dialect == "bash" and i + 1 < len(line) and line[i + 1] in "'\"":
            i = _consume_dollar_construct(line, i, _Frame(), dialect)
            continue
        end = _consume_dollar_construct(line, i, _Frame(), dialect)
        # Named parameters only ($VAR / ${VAR...}). Positional and special
        # parameters ($1, $@, $?, …) are intentionally excluded from quoting
        # policies (matches historic _VAR_EXPANSION behaviour).
        if i + 1 < len(line) and line[i + 1] == "{":
            # ${name...} — require a name start after '{'
            if i + 2 < len(line) and _PARAM_NAME.match(line, i + 2):
                yield Span(i, end)
        elif i + 1 < len(line) and _PARAM_NAME.match(line, i + 1):
            yield Span(i, end)
        i = end


def strip_comment(line: str, *, dialect: Dialect = "bash") -> str:
    """Strip a ``#`` comment that is outside quotes and outside ``$()`` bodies."""
    i = 0
    frame = _Frame()
    while i < len(line):
        if frame.in_single:
            if line[i] == "'":
                frame.in_single = False
            i += 1
            continue
        if frame.in_ansi_c:
            if line[i] == "\\" and i + 1 < len(line):
                i += 2
                continue
            if line[i] == "'":
                frame.in_ansi_c = False
            i += 1
            continue
        if frame.in_double or frame.in_locale_dq:
            if line[i] == "\\":
                i = _skip_escape(line, i, frame)
                continue
            if line[i] == '"':
                frame.in_double = False
                frame.in_locale_dq = False
                i += 1
                continue
            if line[i] == "$" and _dollar_is_special(frame):
                i = _consume_dollar_construct(line, i, frame, dialect)
                continue
            if line[i] == "`":
                i = _consume_backtick(line, i, dialect)
                continue
            i += 1
            continue

        if line[i] == "\\":
            i = _skip_escape(line, i, frame)
            continue
        if (
            dialect == "bash"
            and line[i] == "$"
            and i + 1 < len(line)
            and line[i + 1] == "'"
        ):
            frame.in_ansi_c = True
            i += 2
            continue
        if (
            dialect == "bash"
            and line[i] == "$"
            and i + 1 < len(line)
            and line[i + 1] == '"'
        ):
            frame.in_locale_dq = True
            i += 2
            continue
        if line[i] == "'":
            frame.in_single = True
            i += 1
            continue
        if line[i] == '"':
            frame.in_double = True
            i += 1
            continue
        if line[i] == "`":
            i = _consume_backtick(line, i, dialect)
            continue
        if line[i] == "$":
            i = _consume_dollar_construct(line, i, frame, dialect)
            continue
        if (
            dialect == "bash"
            and line[i] in "<>"
            and i + 1 < len(line)
            and line[i + 1] == "("
        ):
            close = _find_matching_paren(line, i + 1, dialect=dialect)
            i = min(close + 1, len(line))
            continue
        if line[i] == "#":
            return line[:i].rstrip()
        i += 1
    return line


def has_bash_double_bracket(line: str) -> bool:
    """Return whether line contains a ``[[`` conditional (bash)."""
    return "[[" in line


def has_bash_process_substitution(line: str, *, dialect: Dialect = "bash") -> bool:
    if dialect == "sh":
        return False
    for span in iter_command_substitutions(line, dialect=dialect):
        if span.start < len(line) and line[span.start] in "<>":
            return True
    return False


def has_bash_brace_range(line: str) -> bool:
    return bool(_BRACE_RANGE.search(line))


def has_bash_declare(line: str) -> bool:
    return bool(re.search(r"(^|\s)declare\s+", line))
