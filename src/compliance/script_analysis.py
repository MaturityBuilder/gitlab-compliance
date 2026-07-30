"""Predicates for GitLab CI embedded shell script compliance checks."""

from __future__ import annotations

import re
import shlex

from src.compliance.shell_lex import (
    has_bash_brace_range,
    has_bash_declare,
    has_bash_double_bracket,
    has_bash_process_substitution,
    iter_command_substitutions,
    iter_parameter_expansions,
    quote_state_at,
    strip_comment,
)
from src.compliance.stash import get_property

# Match expandable $VAR / ${VAR}; quote safety is decided by _quote_state_at.
_VAR_EXPANSION = re.compile(
    r"(?<!\\)\$(?:\{([A-Za-z_][A-Za-z0-9_]*)\}|([A-Za-z_][A-Za-z0-9_]*))"
)
_ARRAY_STAR = re.compile(r"\$\{?[A-Za-z_][A-Za-z0-9_]*\[\*\]\}?")
_ARRAY_AT = re.compile(r"\$\{[A-Za-z_][A-Za-z0-9_]*\[@\]\}")
_BACKTICKS = re.compile(r"`[^`]+`")
_PIPE = re.compile(r"[^|]\|[^|]")
_CURL_WGET = re.compile(r"\b(curl|wget)\b", re.IGNORECASE)
_CHECKSUM = re.compile(r"\b(sha256sum|shasum|openssl\s+dgst)\b", re.IGNORECASE)
_REMOTE_PIPE = re.compile(
    r"\b(curl|wget)\b[^|\n]*\|\s*(ba)?sh\b",
    re.IGNORECASE,
)
_PIP = re.compile(r"\bpip(?:3)?\s+install\b", re.IGNORECASE)
_APK = re.compile(r"\bapk\s+add\b", re.IGNORECASE)
_APT = re.compile(r"\bapt(?:-get)?\s+install\b", re.IGNORECASE)
_YUM = re.compile(r"\b(?:yum|dnf|microdnf)\s+install\b", re.IGNORECASE)
_NPM_GLOBAL = re.compile(
    r"\b(?:npm\s+install\s+-g|yarn\s+global\s+add)\b", re.IGNORECASE
)
_GO_INSTALL = re.compile(r"\bgo\s+install\b", re.IGNORECASE)
_GIT_CLONE = re.compile(r"\bgit\s+clone\b", re.IGNORECASE)
_DOCKER_CMD = re.compile(r"\bdocker\s+(run|pull|create)\b", re.IGNORECASE)
_DOCKER_FLAGS_WITH_ARG = frozenset(
    {
        "-v",
        "--volume",
        "-p",
        "--publish",
        "-e",
        "--env",
        "--env-file",
        "-w",
        "--workdir",
        "-u",
        "--user",
        "--name",
        "--network",
        "--hostname",
        "--label",
        "-l",
        "--mount",
        "--device",
        "--gpus",
        "--ulimit",
        "--log-driver",
        "--log-opt",
        "--add-host",
        "--dns",
        "--entrypoint",
        "-m",
        "--memory",
        "--cpus",
        "-c",
        "--cpu-shares",
        "--cap-add",
        "--cap-drop",
        "--security-opt",
        "--tmpfs",
        "--sysctl",
        "--platform",
        "--pull",
        "--runtime",
        "--shm-size",
        "--kernel-memory",
    }
)
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
_FUNCTION_DEF = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(\)\s*\{")
_MASK_FAILURE = re.compile(r"\|\|\s*true\b")
_PIPEFAIL = re.compile(r"\bset\s+-o\s+pipefail\b")
_TEST_BRACKET = re.compile(r"\[\s+([^\]]+)\]")
_PATH_WITH_VAR = re.compile(r"(?:^|\s)(?:cd|rm|cp|mv|cat|chmod|chown|mkdir)\s+[^\n]*\$")
_FLOATING_AT_REF = re.compile(
    r"^(?:latest|main|master|develop|dev|HEAD|stable|trunk)$",
    re.IGNORECASE,
)


def _at_version_is_pinned(at_ref: str) -> bool:
    """Return whether an @suffix counts as a pinned package/module version."""
    ref = at_ref.lstrip("@").strip()
    if not ref or _FLOATING_AT_REF.match(ref):
        return False
    if re.match(r"(?:git\+|https?://|file:|ssh://)", ref, re.IGNORECASE):
        return True
    return bool(re.match(r"v?\d", ref))


def _image_tag_is_pinned(tag: str) -> bool:
    """Return whether the tag segment of a container image reference is pinned."""
    if not tag or tag.lower() == "latest":
        return False
    if "/" in tag or tag.isdigit():
        return False
    return True


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
    return strip_comment(line, dialect="bash")


def _quote_state_at(line: str, index: int) -> str:
    """Return quote context at ``index``: ``none``, ``single``, or ``double``.

    Uses a POSIX/bash-aware scanner so expansions inside nested ``$(...)``
    (e.g. ``"$(curl "$HOSTNAME")"``) are judged in the nested quote context.
    """
    return quote_state_at(line, index, dialect="bash")


def _line_has_unquoted_var_expansion(line: str) -> bool:
    """Return True when ``line`` expands a variable outside double quotes."""
    for span in iter_parameter_expansions(line, dialect="bash"):
        if quote_state_at(line, span.start, dialect="bash") == "none":
            return True
    # Fallback for simple $VAR forms the parameter iterator might skip.
    for match in _VAR_EXPANSION.finditer(line):
        if quote_state_at(line, match.start(), dialect="bash") == "none":
            return True
    return False


def _active_lines(entity: dict, field: str = "effective_script") -> list[str]:
    return [
        _strip_comment(line) for line in _script_lines(entity, field) if line.strip()
    ]


def job_has_effective_script(entity: dict) -> bool:
    lines = _active_lines(entity, "effective_script")
    if lines:
        return True
    return bool(_active_lines(entity, "script"))


def job_has_script_field(entity: dict, field: str) -> bool:
    return bool(_active_lines(entity, field))


def script_has_unquoted_variables(entity: dict) -> bool:
    """Return True when any active script line has an unquoted ``$VAR`` expansion."""
    return any(_line_has_unquoted_var_expansion(line) for line in _active_lines(entity))


def _path_argument_span(line: str, cmd_start: int) -> int:
    """Return end index of the path-command arguments, stopping at list operators.

    Stops at unquoted ``&&``, ``||``, ``;``, or ``|`` so later commands on the
    same line (``cd "$HOME" && echo $MSG``) are not treated as path arguments.
    """
    index = cmd_start
    while index < len(line):
        state = _quote_state_at(line, index)
        if state != "none":
            index += 1
            continue
        two = line[index : index + 2]
        if two in {"&&", "||"}:
            return index
        if line[index] in {";", "|"}:
            return index
        index += 1
    return len(line)


def script_has_unquoted_path_variables(entity: dict) -> bool:
    """Return True when path commands expand variables without double quotes."""
    for line in _active_lines(entity):
        cmd_match = _PATH_WITH_VAR.search(line)
        if not cmd_match:
            continue
        span_end = _path_argument_span(line, cmd_match.start())
        # Inspect each expansion in the path-command span only; later quotes on
        # the same line (e.g. ``cd $HOME && echo "done"``) must not clear it.
        for match in _VAR_EXPANSION.finditer(line, cmd_match.start(), span_end):
            if _quote_state_at(line, match.start()) == "none":
                return True
    return False


def script_has_unquoted_command_substitution(entity: dict) -> bool:
    """Return True when ``$(...)`` expands outside double quotes.

    Nested substitutions inside an outer ``"$(...)"`` and literal ``'$(...)'``
    strings are not treated as unquoted expansions. Only top-level
    substitutions are considered for word-splitting risk. Bash process
    substitutions (``<(...)`` / ``>(...)``) are excluded — they are not
    command substitutions for GLCI-BUILTIN-SHELL-QUOTE-03.
    """
    for line in _active_lines(entity):
        for span in iter_command_substitutions(line, dialect="bash", nested=False):
            lead = line[span.start]
            if lead in {"`", "<", ">"}:
                continue
            if quote_state_at(line, span.start, dialect="bash") == "none":
                return True
    return False


def script_has_unsafe_array_expansion(entity: dict) -> bool:
    """Return True when array expansions are unsafe on executed (non-comment) lines."""
    for line in _active_lines(entity):
        for match in _ARRAY_STAR.finditer(line):
            # ``${arr[*]}`` is unsafe whenever it actually expands.
            if quote_state_at(line, match.start(), dialect="bash") != "single":
                return True
        for match in _ARRAY_AT.finditer(line):
            # ``${arr[@]}`` is safe only when expanded inside double quotes.
            if quote_state_at(line, match.start(), dialect="bash") == "none":
                return True
    return False


def script_uses_backticks(entity: dict) -> bool:
    for line in _active_lines(entity):
        for span in iter_command_substitutions(line, dialect="bash"):
            if line[span.start] == "`":
                return True
    return False


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
            expr_offset = match.start(1)
            for var_match in _VAR_EXPANSION.finditer(expr):
                abs_start = expr_offset + var_match.start()
                if _quote_state_at(line, abs_start) == "none":
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
        cmd_match = _RM_RF.search(line)
        if not cmd_match:
            continue
        span_end = _path_argument_span(line, cmd_match.start())
        # Only inspect expansions in the rm arguments; later commands on the
        # same line (``rm -rf "$DIR" && echo $MSG``) must not trip this check.
        for match in _VAR_EXPANSION.finditer(line, cmd_match.start(), span_end):
            if _quote_state_at(line, match.start()) == "none":
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


def _container_image_ref_is_pinned(ref: str) -> bool:
    """Return whether a container image reference includes a tag or digest."""
    cleaned = ref.strip("'\"")
    if not cleaned:
        return True
    lower = cleaned.lower()
    if "@sha256:" in lower:
        return True
    if cleaned.startswith("$"):
        if ":" not in cleaned:
            return False
        return _image_tag_is_pinned(cleaned.rsplit(":", 1)[-1])
    if ":" in cleaned:
        return _image_tag_is_pinned(cleaned.rsplit(":", 1)[-1])
    return False


# Flags that consume the next CLI token (not package names).
_PIP_FLAGS_WITH_ARG = frozenset(
    {
        "-c",
        "--constraint",
        "-f",
        "--find-links",
        "-i",
        "--index-url",
        "--extra-index-url",
        "--trusted-host",
        "-r",
        "--requirement",
        "-t",
        "--target",
        "--root",
        "--prefix",
        "--src",
        "--proxy",
        "--retries",
        "--timeout",
        "--exists-action",
        "--platform",
        "--python-version",
        "--implementation",
        "--abi",
        "--config-settings",
        "--global-option",
        "--no-binary",
        "--only-binary",
        "--progress-bar",
        "--report",
        "--hash",
        "--use-feature",
        "--use-deprecated",
        "--log",
        "--cache-dir",
        "--client-cert",
        "--cert",
        "--key",
    }
)
_APK_FLAGS_WITH_ARG = frozenset(
    {
        "-p",
        "--root",
        "-X",
        "--repository",
        "-t",
        "--virtual",
        "--keys-dir",
        "--arch",
        "--repositories-file",
    }
)
_APT_FLAGS_WITH_ARG = frozenset(
    {
        "-o",
        "--option",
        "-c",
        "--config-file",
        "-t",
        "--target-release",
    }
)
_YUM_FLAGS_WITH_ARG = frozenset(
    {
        "-c",
        "--config",
        "--enablerepo",
        "--disablerepo",
        "--repoid",
        "--setopt",
        "--installroot",
        "--releasever",
        "--downloaddir",
        "--exclude",
        "-x",
    }
)
_RPM_ARCH_SUFFIX = re.compile(
    r"\.(?:x86_64|i[3-6]86|aarch64|armv7hl|ppc64(?:le)?|s390x|noarch|src)$",
    re.IGNORECASE,
)


def _split_command_tokens(segment: str) -> list[str]:
    """Tokenize the argument segment of an install command."""
    try:
        return shlex.split(segment, posix=True)
    except ValueError:
        return segment.split()


def _tokens_after_subcommand(line: str, subcommand: re.Pattern[str]) -> list[str]:
    """Return tokens following a matched subcommand (e.g. ``pip install``)."""
    match = subcommand.search(line)
    if not match:
        return []
    return _split_command_tokens(line[match.end() :])


def _package_tokens(
    tokens: list[str],
    *,
    flags_with_arg: frozenset[str],
    skip_tokens: frozenset[str] | None = None,
) -> list[str]:
    """Extract package tokens, skipping flags and flag arguments."""
    packages: list[str] = []
    skip = skip_tokens or frozenset()
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token in skip:
            index += 1
            continue
        if token.startswith("-"):
            # ``--flag=value`` forms do not consume a following token.
            if "=" in token:
                index += 1
                continue
            if token in flags_with_arg:
                index += 2
                continue
            index += 1
            continue
        packages.append(token)
        index += 1
    return packages


def _pip_package_is_pinned(token: str) -> bool:
    """Return whether one pip package specifier is version-pinned."""
    if "==" in token:
        return True
    if "@" not in token:
        return False
    ref = token.split("@", 1)[1]
    if re.match(r"(?:git\+|https?://|file:|ssh://)", ref, re.IGNORECASE):
        return True
    version = ref.rsplit("@", 1)[-1]
    return _at_version_is_pinned("@" + version)


def _pip_install_line_is_pinned(line: str) -> bool:
    """Return whether a pip/pip3 install line pins every package version."""
    if "--require-hashes" in line:
        return True
    tokens = _tokens_after_subcommand(line, _PIP)
    if not tokens:
        return True
    packages = _package_tokens(tokens, flags_with_arg=_PIP_FLAGS_WITH_ARG)
    if not packages:
        return True
    return all(_pip_package_is_pinned(package) for package in packages)


def _apk_package_is_pinned(token: str) -> bool:
    return "=" in token


def _apk_line_is_pinned(line: str) -> bool:
    """Return whether every apk package on the line has a pinned version."""
    tokens = _tokens_after_subcommand(line, _APK)
    packages = _package_tokens(tokens, flags_with_arg=_APK_FLAGS_WITH_ARG)
    if not packages:
        return True
    return all(_apk_package_is_pinned(package) for package in packages)


def _apt_package_is_pinned(token: str) -> bool:
    return "=" in token


def _apt_line_is_pinned(line: str) -> bool:
    """Return whether every apt package on the line has a pinned version."""
    tokens = _tokens_after_subcommand(line, _APT)
    packages = _package_tokens(tokens, flags_with_arg=_APT_FLAGS_WITH_ARG)
    if not packages:
        return True
    return all(_apt_package_is_pinned(package) for package in packages)


def _yum_package_is_pinned(token: str) -> bool:
    """Return whether an RPM package token includes a version segment.

    Accepts NEVRA-style pins such as ``curl-7.76.1-23.el9`` or ``1:curl-7.76.1``.
    Bare names (including hyphenated names without a version digit) are unpinned.
    """
    cleaned = token.strip("'\"")
    if not cleaned or cleaned.startswith("/"):
        # Local RPM paths are treated as pinned artifacts.
        return bool(cleaned)
    cleaned = _RPM_ARCH_SUFFIX.sub("", cleaned)
    cleaned = re.sub(r"^\d+:", "", cleaned)
    return bool(re.search(r"-\d", cleaned))


def _yum_line_is_pinned(line: str) -> bool:
    """Return whether every yum/dnf/microdnf package on the line is version-pinned."""
    tokens = _tokens_after_subcommand(line, _YUM)
    packages = _package_tokens(tokens, flags_with_arg=_YUM_FLAGS_WITH_ARG)
    if not packages:
        return True
    return all(_yum_package_is_pinned(package) for package in packages)


def _npm_package_is_pinned(token: str) -> bool:
    """Return whether one npm/yarn global package specifier is version-pinned."""
    if token.startswith("@"):
        if token.count("@") < 2:
            return False
        version = token.rsplit("@", 1)[-1]
        return _at_version_is_pinned("@" + version)
    if "@" in token:
        version = token.rsplit("@", 1)[-1]
        return _at_version_is_pinned("@" + version)
    return False


def _npm_line_is_pinned(line: str) -> bool:
    """Return whether every npm/yarn global package on the line is version-pinned."""
    tokens = _tokens_after_subcommand(line, _NPM_GLOBAL)
    packages = [
        token
        for token in tokens
        if not token.startswith("-") and token not in {"-g", "global", "add"}
    ]
    if not packages:
        return True
    return all(_npm_package_is_pinned(package) for package in packages)


def _is_volume_mount(token: str) -> bool:
    if ":" not in token:
        return False
    if re.match(
        r"^[\w][\w./-]*(?:@sha256:[a-f0-9]{64}|:[\w][\w.-]+)$",
        token,
        re.IGNORECASE,
    ):
        return False
    host, _container = token.split(":", 1)
    return host.startswith(("./", "/", "$", ".")) or host.isdigit()


def _extract_docker_image_from_run(rest: str) -> list[str]:
    try:
        tokens = shlex.split(rest, posix=True)
    except ValueError:
        return []
    skip_next = False
    for token in tokens:
        if skip_next:
            skip_next = False
            continue
        if token in _DOCKER_FLAGS_WITH_ARG:
            skip_next = True
            continue
        if token.startswith("--") and "=" in token:
            continue
        if token.startswith("-"):
            continue
        if _is_volume_mount(token):
            continue
        return [token]
    return []


def _docker_image_refs_on_line(line: str) -> list[str]:
    refs: list[str] = []
    for match in re.finditer(
        r"\bdocker\s+pull\s+(?:--[\w-]+\s+)*([\"']?)([^\s\"']+)\1",
        line,
        re.IGNORECASE,
    ):
        refs.append(match.group(2))
    run_match = re.search(r"\bdocker\s+run\b\s+(.+)$", line, re.IGNORECASE)
    if run_match:
        refs.extend(_extract_docker_image_from_run(run_match.group(1)))
    create_match = re.search(r"\bdocker\s+create\b\s+(.+)$", line, re.IGNORECASE)
    if create_match:
        refs.extend(_extract_docker_image_from_run(create_match.group(1)))
    return refs


def script_has_unpinned_pip(entity: dict) -> bool:
    for line in _active_lines(entity):
        if not _PIP.search(line):
            continue
        if not _pip_install_line_is_pinned(line):
            return True
    return False


def script_has_unpinned_docker_image(entity: dict) -> bool:
    for line in _active_lines(entity):
        if not _DOCKER_CMD.search(line):
            continue
        for ref in _docker_image_refs_on_line(line):
            if not _container_image_ref_is_pinned(ref):
                return True
    return False


def script_has_unpinned_apk(entity: dict) -> bool:
    for line in _active_lines(entity):
        if not _APK.search(line):
            continue
        if not _apk_line_is_pinned(line):
            return True
    return False


def script_has_unpinned_apt(entity: dict) -> bool:
    for line in _active_lines(entity):
        if not _APT.search(line):
            continue
        if not _apt_line_is_pinned(line):
            return True
    return False


def script_has_unpinned_yum(entity: dict) -> bool:
    """Return True when yum/dnf/microdnf install lines have unpinned packages."""
    for line in _active_lines(entity):
        if not _YUM.search(line):
            continue
        if not _yum_line_is_pinned(line):
            return True
    return False


def script_has_unpinned_npm(entity: dict) -> bool:
    for line in _active_lines(entity):
        if not _NPM_GLOBAL.search(line):
            continue
        if not _npm_line_is_pinned(line):
            return True
    return False


def script_has_unpinned_go_install(entity: dict) -> bool:
    for line in _active_lines(entity):
        if not _GO_INSTALL.search(line):
            continue
        if "@" not in line:
            return True
        at_ref = line.rsplit("@", 1)[-1].split()[0]
        if not _at_version_is_pinned("@" + at_ref):
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


def _line_has_bashism(line: str) -> bool:
    """Return True when ``line`` uses a bash-only construct we flag for PORT."""
    return bool(
        has_bash_double_bracket(line)
        or "source " in line
        or has_bash_process_substitution(line, dialect="bash")
        or has_bash_brace_range(line)
        or has_bash_declare(line)
    )


def script_has_bashisms(entity: dict) -> bool:
    text = _joined_script(entity)
    if has_bash_double_bracket(text) or "source " in text:
        return True
    return any(_line_has_bashism(line) for line in _active_lines(entity))


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


def _first_active_line(entity: dict, line_predicate) -> str | None:
    """Return the first active script line matching ``line_predicate``."""
    for line in _active_lines(entity):
        if line_predicate(line):
            return line.strip()
    return None


def _clip_evidence(text: str, limit: int = 200) -> str:
    snippet = " ".join(text.split())
    if len(snippet) > limit:
        return snippet[: limit - 3] + "..."
    return snippet


def evidence_unquoted_variables(entity: dict) -> str | None:
    return _first_active_line(entity, _line_has_unquoted_var_expansion)


def evidence_unquoted_path_variables(entity: dict) -> str | None:
    for line in _active_lines(entity):
        cmd_match = _PATH_WITH_VAR.search(line)
        if not cmd_match:
            continue
        span_end = _path_argument_span(line, cmd_match.start())
        for match in _VAR_EXPANSION.finditer(line, cmd_match.start(), span_end):
            if _quote_state_at(line, match.start()) == "none":
                return line.strip()
    return None


def evidence_unquoted_command_substitution(entity: dict) -> str | None:
    """Return the first line with unquoted ``$(...)`` (same rules as the predicate)."""
    for line in _active_lines(entity):
        for span in iter_command_substitutions(line, dialect="bash", nested=False):
            lead = line[span.start]
            if lead in {"`", "<", ">"}:
                continue
            if quote_state_at(line, span.start, dialect="bash") == "none":
                return line.strip()
    return None


def evidence_unsafe_array_expansion(entity: dict) -> str | None:
    for line in _active_lines(entity):
        for match in _ARRAY_STAR.finditer(line):
            if _quote_state_at(line, match.start()) != "single":
                return line.strip()
        for match in _ARRAY_AT.finditer(line):
            if _quote_state_at(line, match.start()) == "none":
                return line.strip()
    return None


def evidence_nested_backticks(entity: dict) -> str | None:
    text = _joined_script(entity)
    match = re.search(r"`[^`]*`[^`]*`", text)
    if not match:
        return None
    return match.group(0)


def evidence_missing_strict_mode(entity: dict) -> str | None:
    if script_enables_strict_mode(entity):
        return None
    lines = _active_lines(entity)
    if not lines:
        return None
    return _clip_evidence("; ".join(lines[:3]))


def evidence_masked_failure(entity: dict) -> str | None:
    return _first_active_line(entity, lambda line: bool(_MASK_FAILURE.search(line)))


def evidence_insecure_temp_files(entity: dict) -> str | None:
    if _MKTEMP.search(_joined_script(entity)):
        return None
    return _first_active_line(
        entity,
        lambda line: bool(re.search(r">\s*/tmp/[A-Za-z0-9._-]+", line) or "$$" in line),
    )


def evidence_dangerous_rm(entity: dict) -> str | None:
    if _RM_RF_ROOT.search(_joined_script(entity)):
        return _first_active_line(entity, lambda line: bool(_RM_RF_ROOT.search(line)))
    for line in _active_lines(entity):
        cmd_match = _RM_RF.search(line)
        if not cmd_match:
            continue
        span_end = _path_argument_span(line, cmd_match.start())
        for match in _VAR_EXPANSION.finditer(line, cmd_match.start(), span_end):
            if _quote_state_at(line, match.start()) == "none":
                return line.strip()
    return None


def evidence_backticks(entity: dict) -> str | None:
    return _first_active_line(entity, lambda line: bool(_BACKTICKS.search(line)))


def evidence_bashism_in_posix_test(entity: dict) -> str | None:
    return _first_active_line(
        entity, lambda line: bool(re.search(r"\[\s+[^\]]*(==|-n\s+\$)", line))
    )


def evidence_unquoted_test_variables(entity: dict) -> str | None:
    for line in _active_lines(entity):
        for match in _TEST_BRACKET.finditer(line):
            expr = match.group(1)
            expr_offset = match.start(1)
            for var_match in _VAR_EXPANSION.finditer(expr):
                abs_start = expr_offset + var_match.start()
                if _quote_state_at(line, abs_start) == "none":
                    return line.strip()
    return None


def evidence_pipeline_without_pipefail(entity: dict) -> str | None:
    if not script_has_pipeline(entity) or script_has_pipefail(entity):
        return None
    return _first_active_line(entity, lambda line: bool(_PIPE.search(line)))


def evidence_eval(entity: dict) -> str | None:
    return _first_active_line(entity, lambda line: bool(_EVAL.search(line)))


def evidence_remote_pipe(entity: dict) -> str | None:
    return _first_active_line(entity, lambda line: bool(_REMOTE_PIPE.search(line)))


def evidence_hardcoded_secrets(entity: dict) -> str | None:
    return _first_active_line(entity, lambda line: bool(_SECRET.search(line)))


def evidence_download_without_checksum(entity: dict) -> str | None:
    lines = _active_lines(entity)
    for index, line in enumerate(lines):
        if not _CURL_WGET.search(line):
            continue
        if _REMOTE_PIPE.search(line):
            continue
        window = "\n".join(lines[max(0, index - 3) : index + 4])
        if not _CHECKSUM.search(window):
            return line.strip()
    return None


def evidence_unpinned_manager(entity: dict, manager: str) -> str | None:
    checkers = {
        "apk": (_APK, _apk_line_is_pinned),
        "pip": (_PIP, _pip_install_line_is_pinned),
        "apt": (_APT, _apt_line_is_pinned),
        "yum": (_YUM, _yum_line_is_pinned),
        "npm": (_NPM_GLOBAL, _npm_line_is_pinned),
    }
    if manager == "go":
        for line in _active_lines(entity):
            if not _GO_INSTALL.search(line):
                continue
            if "@" not in line:
                return line.strip()
            at_ref = line.rsplit("@", 1)[-1].split()[0]
            if not _at_version_is_pinned("@" + at_ref):
                return line.strip()
        return None
    pair = checkers.get(manager)
    if not pair:
        return None
    pattern, is_pinned = pair
    for line in _active_lines(entity):
        if pattern.search(line) and not is_pinned(line):
            return line.strip()
    return None


def evidence_unpinned_docker(entity: dict) -> str | None:
    for line in _active_lines(entity):
        if not _DOCKER_CMD.search(line):
            continue
        for ref in _docker_image_refs_on_line(line):
            if not _container_image_ref_is_pinned(ref):
                return line.strip()
    return None


def evidence_unverified_git_clone(entity: dict) -> str | None:
    lines = _active_lines(entity)
    for index, line in enumerate(lines):
        if not _GIT_CLONE.search(line):
            continue
        window = "\n".join(lines[index : index + 5])
        if not re.search(r"\bgit\s+checkout\b|\bgit\s+reset\s+--hard\b", window):
            return line.strip()
    return None


def evidence_curl_missing_fail(entity: dict) -> str | None:
    return _first_active_line(
        entity,
        lambda line: bool(_CURL_CMD.search(line) and not _CURL_FAIL.search(line)),
    )


def evidence_deprecated_ci_build(entity: dict) -> str | None:
    return _first_active_line(entity, lambda line: bool(_CI_BUILD.search(line)))


def evidence_unresolved_references(entity: dict) -> str | None:
    refs = get_property(entity, "unresolved_script_references")
    if isinstance(refs, list) and refs:
        return str(refs[0])
    provenance = get_property(entity, "script_provenance")
    if isinstance(provenance, list):
        for item in provenance:
            if isinstance(item, dict) and item.get("origin") == "unresolved_reference":
                return str(
                    item.get("via") or item.get("text") or "unresolved_reference"
                )
    return None


def evidence_invalid_shebang(entity: dict) -> str | None:
    lines = _script_lines(entity)
    if not lines or not lines[0].startswith("#!"):
        return None
    if script_shebang_is_valid(entity):
        return None
    return lines[0].strip()


def evidence_bashisms_without_bash(entity: dict) -> str | None:
    if not script_bashisms_without_bash_shebang(entity):
        return None
    lines = _script_lines(entity)
    shebang = lines[0].strip() if lines else ""
    hit = _first_active_line(entity, _line_has_bashism)
    if hit and shebang:
        return f"{shebang}; {hit}"
    return hit or shebang or None  # pragma: no cover — bashism True ⇒ hit+shebang set


def evidence_posix_bashisms(entity: dict) -> str | None:
    if not script_posix_shebang_with_bashisms(entity):
        return None
    return evidence_bashisms_without_bash(entity)


def evidence_chmod_777(entity: dict) -> str | None:
    return _first_active_line(entity, lambda line: bool(_CHMOD_777.search(line)))


def format_script_violation(
    entity: dict, message: str, *, found: str | None = None
) -> str:
    name = entity.get("name", "<job>")
    source = entity.get("source_file", "")
    line = entity.get("line", 0)
    chain = get_property(entity, "extends_chain") or []
    via = ""
    if isinstance(chain, list) and chain:
        via = " via: " + " → ".join(f"extends:{item}" for item in chain)
    location = f"{source}:{line}" if source else ""
    detail = message
    if found:
        detail = f"{message}; found: {_clip_evidence(found)}"
    return f"Job '{name}' {location}: {detail}{via}".strip()
