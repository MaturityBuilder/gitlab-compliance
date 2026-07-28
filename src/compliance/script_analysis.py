"""Predicates for GitLab CI embedded shell script compliance checks."""

from __future__ import annotations

import re
import shlex

from src.compliance.stash import get_property

_UNQUOTED_VAR = re.compile(
    r"(?<![\"'\\])\$(?:\{([A-Za-z_][A-Za-z0-9_]*)\}|([A-Za-z_][A-Za-z0-9_]*))"
)
_ARRAY_STAR = re.compile(r"\$\{?[A-Za-z_][A-Za-z0-9_]*\[\*\]\}?")
_BACKTICKS = re.compile(r"`[^`]+`")
_CMD_SUB = re.compile(r"\$\([^)]+\)")
_PIPE = re.compile(r"[^|]\|[^|]")
_CURL_WGET = re.compile(r"\b(curl|wget)\b", re.IGNORECASE)
_CHECKSUM = re.compile(r"\b(sha256sum|shasum|openssl\s+dgst)\b", re.IGNORECASE)
_REMOTE_PIPE = re.compile(
    r"\b(curl|wget)\b[^|\n]*\|\s*(ba)?sh\b",
    re.IGNORECASE,
)
_PIP = re.compile(r"(?:\bpython(?:3)?\s+-m\s+)?\bpip(?:3)?\s+install\b", re.IGNORECASE)
_APK = re.compile(r"\bapk\s+add\b", re.IGNORECASE)
_APT = re.compile(r"\bapt(?:-get)?\s+install\b", re.IGNORECASE)
_NPM_GLOBAL = re.compile(
    r"\b(?:npm\s+(?:install|i)\s+(?:-g|--global)\b|npm\s+(?:-g|--global)\s+(?:install|i)\b|"
    r"yarn\s+global\s+add|pnpm\s+(?:add|install)\s+(?:-g|--global)\b|"
    r"pnpm\s+(?:-g|--global)\s+(?:add|install)\b)\b",
    re.IGNORECASE,
)
_GO_INSTALL = re.compile(r"\bgo\s+install\b", re.IGNORECASE)
_COMMAND_SPLIT = re.compile(r"\s*(?:&&|;)\s*")
_APT_VALUE_FLAGS = frozenset(
    {"-o", "--option", "-t", "--target", "-t", "--target-release"}
)
_APK_VALUE_FLAGS = frozenset(
    {"-p", "--repository", "-X", "--repository", "-U", "--upgrade"}
)
_PIP_VALUE_FLAGS = frozenset(
    {
        "-r",
        "--requirement",
        "-c",
        "--constraint",
        "-i",
        "--index-url",
        "--extra-index-url",
        "--find-links",
        "-f",
        "--editable",
        "-e",
        "--prefix",
        "--root",
        "--target",
        "--src",
    }
)
_GIT_CLONE = re.compile(r"\bgit\s+clone\b", re.IGNORECASE)
_EVAL = re.compile(r"(^|\s)eval\s")
_RM_RF_ROOT = re.compile(r"\brm\s+(-[a-zA-Z]*r[a-zA-Z]*f|-[a-zA-Z]*f[a-zA-Z]*r)\s+/")
_RM_RF = re.compile(r"\brm\s+(-[a-zA-Z]*r[a-zA-Z]*f|-[a-zA-Z]*f[a-zA-Z]*r)\b")
_MKTEMP = re.compile(r"\bmktemp\b")
_CHMOD_777 = re.compile(r"\bchmod\s+777\b")
_SECRET = re.compile(
    r"(glpat-[A-Za-z0-9_-]+|AKIA[0-9A-Z]{16}|password\s*=\s*['\"][^'\"]+['\"]|"
    r"Bearer\s+eyJ[A-Za-z0-9_-]+)",
    re.IGNORECASE,
)
_CI_BUILD = re.compile(r"\$\{?CI_BUILD_[A-Z0-9_]+\}?")
# Match curl as a command invocation, not package names like ``apk add curl=...``.
_CURL_CMD = re.compile(r"(?:^|[;&|]|\b(?:then|else|do)\b)\s*curl\s+")
_CURL_FAIL = re.compile(
    r"(?:^|[;&|]|\b(?:then|else|do)\b)\s*curl\s+[^\n]*(--fail|-[a-zA-Z]*f[a-zA-Z]*)"
)
_VALID_SHEBANG = re.compile(
    r"^#!\s*(/usr/bin/env\s+(bash|sh)|/bin/(bash|sh)|/usr/bin/(bash|sh))\b"
)
_BASHISM_DOUBLE_BRACKET = re.compile(r"\[\[")
_FUNCTION_DEF = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(\)\s*\{")
_MASK_FAILURE = re.compile(r"\|\|\s*true\b")
_PIPEFAIL = re.compile(r"\bset\s+-o\s+pipefail\b")
_TEST_BRACKET = re.compile(r"\[\s+([^\]]+)\]")
_PATH_WITH_VAR = re.compile(r"(?:^|\s)(?:cd|rm|cp|mv|cat|chmod|chown|mkdir)\s+[^\n]*\$")


def _script_lines(entity: dict, field: str = "effective_script") -> list[str]:
    value = get_property(entity, field)
    if value is None:
        value = get_property(entity, "script")
    if value is None:
        return []
    if isinstance(value, list):
        lines: list[str] = []
        for item in value:
            if item is None:
                continue
            lines.extend(str(item).splitlines() or [str(item)])
        return lines
    return str(value).splitlines() or [str(value)]


def _joined_script(entity: dict, field: str = "effective_script") -> str:
    return "\n".join(_script_lines(entity, field))


def _strip_comment(line: str) -> str:
    in_single = False
    in_double = False
    for index, char in enumerate(line):
        if char == "'" and not in_double:
            in_single = not in_single
        elif char == '"' and not in_single:
            in_double = not in_double
        elif char == "#" and not in_single and not in_double:
            return line[:index].rstrip()
    return line


def _active_lines(entity: dict, field: str = "effective_script") -> list[str]:
    return [
        _strip_comment(line) for line in _script_lines(entity, field) if line.strip()
    ]


def _split_commands(line: str) -> list[str]:
    parts = _COMMAND_SPLIT.split(line.strip())
    return [part.strip() for part in parts if part.strip()]


def _install_tokens(segment: str, install_pattern: re.Pattern[str]) -> list[str]:
    match = install_pattern.search(segment)
    if not match:
        return []
    tail = segment[match.end() :].strip()
    if not tail:
        return []
    try:
        return shlex.split(tail, posix=True)
    except ValueError:
        return tail.split()


def _skip_flag_tokens(
    tokens: list[str],
    *,
    value_flags: frozenset[str] | None = None,
    virtual_flag: str | None = None,
) -> list[str]:
    value_flags = value_flags or frozenset()
    packages: list[str] = []
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token == virtual_flag:
            index += 2
            continue
        if token in value_flags:
            index += 2
            continue
        if token.startswith("-") and "=" not in token:
            index += 1
            continue
        packages.append(token)
        index += 1
    return packages


def _is_version_pinned_token(token: str, manager: str) -> bool:
    if manager in {"apt", "apk"}:
        return "=" in token and not token.startswith("=")
    if manager == "pip":
        if token in {".", "./", ".."}:
            return True
        if token.startswith(("-", ".")):
            return True
        return "==" in token or "@" in token
    if manager == "npm":
        if "@" not in token:
            return False
        version = token.rsplit("@", 1)[-1]
        return bool(version) and version.lower() != "latest"
    if manager == "go":
        if "@" not in token:
            return False
        version = token.rsplit("@", 1)[-1]
        return bool(version) and version.lower() != "latest"
    return False


def _has_unpinned_packages(
    line: str,
    install_pattern: re.Pattern[str],
    manager: str,
    *,
    value_flags: frozenset[str] | None = None,
    virtual_flag: str | None = None,
    allow_requirements: bool = False,
) -> bool:
    for segment in _split_commands(line):
        if not install_pattern.search(segment):
            continue
        tokens = _install_tokens(segment, install_pattern)
        if allow_requirements and any(
            token in {"-r", "--requirement"} for token in tokens
        ):
            continue
        packages = _skip_flag_tokens(
            tokens,
            value_flags=value_flags,
            virtual_flag=virtual_flag,
        )
        if not packages:
            continue
        if any(not _is_version_pinned_token(package, manager) for package in packages):
            return True
    return False


def job_has_effective_script(entity: dict) -> bool:
    lines = _active_lines(entity, "effective_script")
    if lines:
        return True
    return bool(_active_lines(entity, "script"))


def job_has_script_field(entity: dict, field: str) -> bool:
    return bool(_active_lines(entity, field))


def script_has_unquoted_variables(entity: dict) -> bool:
    for line in _active_lines(entity):
        for match in _UNQUOTED_VAR.finditer(line):
            start = match.start()
            # Allow $1 positional and special params already excluded by pattern.
            prefix = line[:start]
            if prefix.count('"') % 2 == 1:
                continue
            return True
    return False


def script_has_unquoted_path_variables(entity: dict) -> bool:
    for line in _active_lines(entity):
        cmd_match = _PATH_WITH_VAR.search(line)
        if not cmd_match:
            continue
        segment = line[cmd_match.start() :]
        if _UNQUOTED_VAR.search(segment) and '"' not in segment:
            return True
    return False


def script_has_unquoted_command_substitution(entity: dict) -> bool:
    for line in _active_lines(entity):
        for match in _CMD_SUB.finditer(line):
            start = match.start()
            if start == 0 or line[start - 1] != '"':
                return True
    return False


def script_has_unsafe_array_expansion(entity: dict) -> bool:
    text = _joined_script(entity)
    if _ARRAY_STAR.search(text):
        return True
    # Detect ${arr[@]} without surrounding quotes.
    for match in re.finditer(r"\$\{[A-Za-z_][A-Za-z0-9_]*\[@\]\}", text):
        start = match.start()
        end = match.end()
        if start == 0 or text[start - 1] != '"' or end >= len(text) or text[end] != '"':
            return True
    return False


def script_uses_backticks(entity: dict) -> bool:
    return bool(_BACKTICKS.search(_joined_script(entity)))


def script_has_nested_backticks(entity: dict) -> bool:
    return bool(re.search(r"`[^`]*`[^`]*`", _joined_script(entity)))


def script_has_pipeline(entity: dict) -> bool:
    return any(_PIPE.search(line) for line in _active_lines(entity))


def script_has_pipefail(entity: dict) -> bool:
    text = _joined_script(entity)
    if "set -euo pipefail" in text or "set -eo pipefail" in text:
        return True
    return bool(_PIPEFAIL.search(text))


def script_enables_strict_mode(entity: dict) -> bool:
    text = _joined_script(entity)
    has_e = bool(re.search(r"\bset\s+-[a-zA-Z]*e", text) or "set -euo pipefail" in text)
    has_u = bool(re.search(r"\bset\s+-[a-zA-Z]*u", text) or "set -euo pipefail" in text)
    has_pipefail = bool(_PIPEFAIL.search(text) or "set -euo pipefail" in text)
    return has_e and has_u and has_pipefail


def script_is_multiline(entity: dict) -> bool:
    return len(_active_lines(entity)) > 1


def script_masks_failures(entity: dict) -> bool:
    return bool(_MASK_FAILURE.search(_joined_script(entity)))


def script_defines_functions(entity: dict) -> bool:
    return bool(_FUNCTION_DEF.search(_joined_script(entity)))


def script_functions_mask_failures(entity: dict) -> bool:
    text = _joined_script(entity)
    if not _FUNCTION_DEF.search(text):
        return False
    return bool(_MASK_FAILURE.search(text))


def script_has_unquoted_test_variables(entity: dict) -> bool:
    for line in _active_lines(entity):
        for match in _TEST_BRACKET.finditer(line):
            expr = match.group(1)
            for var_match in _UNQUOTED_VAR.finditer(expr):
                prefix = expr[: var_match.start()]
                if prefix.count('"') % 2 == 1:
                    continue
                return True
    return False


def script_has_bashism_in_posix_test(entity: dict) -> bool:
    for line in _active_lines(entity):
        if re.search(r"\[\s+[^\]]*(==|-n\s+\$)", line):
            return True
    return False


def script_uses_eval(entity: dict) -> bool:
    return any(_EVAL.search(line) for line in _active_lines(entity))


def script_has_remote_pipe_to_shell(entity: dict) -> bool:
    return bool(_REMOTE_PIPE.search(_joined_script(entity)))


def script_has_hardcoded_secrets(entity: dict) -> bool:
    return bool(_SECRET.search(_joined_script(entity)))


def script_has_chmod_777(entity: dict) -> bool:
    return bool(_CHMOD_777.search(_joined_script(entity)))


def script_has_dangerous_rm(entity: dict) -> bool:
    text = _joined_script(entity)
    if _RM_RF_ROOT.search(text):
        return True
    for line in _active_lines(entity):
        if _RM_RF.search(line) and _UNQUOTED_VAR.search(line) and '"' not in line:
            return True
    return False


def script_uses_insecure_temp_files(entity: dict) -> bool:
    text = _joined_script(entity)
    if _MKTEMP.search(text):
        return False
    return bool(re.search(r">\s*/tmp/[A-Za-z0-9._-]+", text) or "$$" in text)


def script_uses_mktemp_when_needed(entity: dict) -> bool:
    return not script_uses_insecure_temp_files(entity)


def script_downloads_without_checksum(entity: dict) -> bool:
    lines = _active_lines(entity)
    for index, line in enumerate(lines):
        if not _CURL_WGET.search(line):
            continue
        if _REMOTE_PIPE.search(line):
            continue
        window = "\n".join(lines[max(0, index - 3) : index + 4])
        if not _CHECKSUM.search(window):
            return True
    return False


def script_has_unpinned_pip(entity: dict) -> bool:
    for line in _active_lines(entity):
        if not _PIP.search(line):
            continue
        if "--require-hashes" in line:
            continue
        if _has_unpinned_packages(
            line,
            _PIP,
            "pip",
            value_flags=_PIP_VALUE_FLAGS,
            allow_requirements=True,
        ):
            return True
    return False


def script_has_unpinned_apk(entity: dict) -> bool:
    for line in _active_lines(entity):
        if not _APK.search(line):
            continue
        if _has_unpinned_packages(
            line,
            _APK,
            "apk",
            value_flags=_APK_VALUE_FLAGS,
            virtual_flag="--virtual",
        ):
            return True
    return False


def script_has_unpinned_apt(entity: dict) -> bool:
    for line in _active_lines(entity):
        if not _APT.search(line):
            continue
        if _has_unpinned_packages(
            line,
            _APT,
            "apt",
            value_flags=_APT_VALUE_FLAGS,
        ):
            return True
    return False


def script_has_unpinned_npm(entity: dict) -> bool:
    for line in _active_lines(entity):
        if not _NPM_GLOBAL.search(line):
            continue
        if _has_unpinned_packages(line, _NPM_GLOBAL, "npm"):
            return True
    return False


def script_has_unpinned_go_install(entity: dict) -> bool:
    for line in _active_lines(entity):
        if not _GO_INSTALL.search(line):
            continue
        tokens = _install_tokens(line, _GO_INSTALL)
        if not tokens:
            return True
        for token in _skip_flag_tokens(tokens):
            if not _is_version_pinned_token(token, "go"):
                return True
    return False


def script_has_unverified_git_clone(entity: dict) -> bool:
    lines = _active_lines(entity)
    for index, line in enumerate(lines):
        if not _GIT_CLONE.search(line):
            continue
        window = "\n".join(lines[index : index + 5])
        if not re.search(r"\bgit\s+checkout\b|\bgit\s+reset\s+--hard\b", window):
            return True
    return False


def script_curl_missing_fail(entity: dict) -> bool:
    for line in _active_lines(entity):
        if _CURL_CMD.search(line) and not _CURL_FAIL.search(line):
            return True
    return False


def script_uses_deprecated_ci_build_vars(entity: dict) -> bool:
    return bool(_CI_BUILD.search(_joined_script(entity)))


def script_has_unresolved_references(entity: dict) -> bool:
    refs = get_property(entity, "unresolved_script_references")
    if isinstance(refs, list):
        return len(refs) > 0
    provenance = get_property(entity, "script_provenance")
    if isinstance(provenance, list):
        return any(
            isinstance(item, dict) and item.get("origin") == "unresolved_reference"
            for item in provenance
        )
    return False


def script_has_shebang(entity: dict) -> bool:
    lines = _script_lines(entity)
    return bool(lines and lines[0].startswith("#!"))


def script_shebang_is_valid(entity: dict) -> bool:
    lines = _script_lines(entity)
    if not lines or not lines[0].startswith("#!"):
        return True
    return bool(_VALID_SHEBANG.match(lines[0].strip()))


def script_has_bashisms(entity: dict) -> bool:
    text = _joined_script(entity)
    return bool(_BASHISM_DOUBLE_BRACKET.search(text) or "source " in text)


def script_shebang_is_sh(entity: dict) -> bool:
    lines = _script_lines(entity)
    if not lines or not lines[0].startswith("#!"):
        return False
    return bool(re.search(r"\bsh\b", lines[0]) and "bash" not in lines[0])


def script_bashisms_without_bash_shebang(entity: dict) -> bool:
    """Fail only when a shebang is present and does not allow bash."""
    if not script_has_bashisms(entity):
        return False
    lines = _script_lines(entity)
    if not lines or not lines[0].startswith("#!"):
        return False
    return "bash" not in lines[0]


def script_posix_shebang_with_bashisms(entity: dict) -> bool:
    return script_shebang_is_sh(entity) and script_has_bashisms(entity)


def format_script_violation(entity: dict, message: str) -> str:
    name = entity.get("name", "<job>")
    source = entity.get("source_file", "")
    line = entity.get("line", 0)
    chain = get_property(entity, "extends_chain") or []
    via = ""
    if isinstance(chain, list) and chain:
        via = " via: " + " → ".join(f"extends:{item}" for item in chain)
    location = f"{source}:{line}" if source else ""
    return f"Job '{name}' {location}: {message}{via}".strip()
