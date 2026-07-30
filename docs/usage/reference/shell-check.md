# shell-check

Run packaged Gherkin shell standards for CI scripts (not the ShellCheck tool).

    Validates before_script/script/after_script using builtin GLCI-SHELL-* policies.
    Does not install, detect, or invoke the external ShellCheck binary.

<!-- MANUAL DOCS:START -->

## See it in action

Offline demos use the fixtures under `docs/demos/fixtures/shell-check/`.
Regenerate with `bash scripts/record-demos.sh offline` (see
[demos README](../../demos/README.md)).

### Console report

![gitlab-compliance shell-check console report](../../demos/gifs/shell-check-console.gif)

### Markdown report

![gitlab-compliance shell-check markdown report](../../demos/gifs/shell-check-markdown.gif)

## What it checks

Packaged policies under `src/compliance/builtin_policies/shell/` express
ShellCheck-inspired standards as BDD scenarios with `GLCI-SHELL-*` IDs:

- Quoting, error handling, file operations, command substitution
- Conditionals, pipelines, security, portability
- GitLab CI pinning (package managers, checksums, docker image tags), CI hygiene,
  `!reference` resolution

Scripts are composed from `extends`, YAML anchors, and `!reference` before
scenarios run. Hidden jobs (names starting with `.`) are included.

### Quoting and expansions

Variable and command-substitution checks use a POSIX-aligned scanner
([Shell Command Language §2.2–2.3](https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html)):
characters inside `$(...)` are **not** affected by enclosing double quotes, so
this is correctly treated as quoted:

```bash
check="$(curl "$HOSTNAME" | jq -r '.message')"
```

Bash CI scripts (no shebang, or `#!/bin/bash`) also recognize common bash forms
from typical cheat sheets (`${foo:-default}`, `[[ ... ]]`, process substitution
`<(...)`, `$'...'`). Under `#!/bin/sh`, those remain portability bashisms.

## Quick start

```bash
gitlab-compliance shell-check -p .gitlab-ci.yml
```

Show only failures (keeps summary counts):

```bash
gitlab-compliance shell-check -p .gitlab-ci.yml --failures-only
```

Include the offending script value that triggered each failure:

```bash
gitlab-compliance shell-check -p .gitlab-ci.yml --failures-only -v
```

Run specific policies by ID, glob, or feature-file stem:

```bash
gitlab-compliance shell-check -p .gitlab-ci.yml -P GLCI-SHELL-PIN-003
gitlab-compliance shell-check -p .gitlab-ci.yml -P 'GLCI-SHELL-PIN*,GLCI-SHELL-QUOTE-001'
gitlab-compliance shell-check -p .gitlab-ci.yml -P shell-quoting
```

Markdown report:

```bash
gitlab-compliance shell-check -p .gitlab-ci.yml --format markdown -o SHELL-CHECK.md
```

JUnit report for GitLab CI test artifacts:

```bash
gitlab-compliance shell-check -p .gitlab-ci.yml --format junit -o SHELL-CHECK.xml
```

```yaml
# .gitlab-ci.yml excerpt
script:
  - gitlab-compliance shell-check -p .gitlab-ci.yml --format junit -o SHELL-CHECK.xml
artifacts:
  reports:
    junit: SHELL-CHECK.xml
```

Also available via `check --with-shell-check` (adds packaged `GLCI-SHELL-*`
policies alongside your `-f` directory). `--with-builtin` does **not** include
shell policies; add `--with-shell-check` explicitly when needed.

See [Shell pinning examples](../../examples/shell-pinning.md) for per-manager
Gherkin scenarios (`apk`, `apt`, `yum`/`dnf`, `pip`, `npm`, `go`, `docker`).

## Include resolution and GitLab API

`shell-check` uses the same include and API flags as [`check`](check.md):

| Include type | Resolved locally | Fetched with token / HTTP |
| --- | --- | --- |
| `local:` | Yes (`--include-nested`, default on) | N/A |
| `remote:` | No | Yes (`--resolve-external-includes`, default auto) |
| `project:` | No | Yes (requires `--token` or `GITLAB_TOKEN`) |
| `component:` | No | Not yet (reported as coverage gap) |
| `template:` | No | Not yet (reported as coverage gap) |

Flags:

- `--include-nested` / `--no-include-nested` — walk nested **local** `include:` files (default: on)
- `--max-include-depth` — limit include nesting depth
- `--resolve-external-includes` / `--no-resolve-external-includes` — fetch `remote:` and `project:` YAML (default: **auto** — remote always, project when a token is available)
- `--gitlab-url`, `--token`, `--project`, `--group` — GitLab API connection (same env fallbacks as `check`: `GITLAB_TOKEN`, `CI_JOB_TOKEN`, `CI_PROJECT_PATH`)
- `--strict` — fail API-backed scenarios when credentials are missing (default: skip)
- `--failures-only` — show only failed policies (summary counts are kept; passed/skipped sections are omitted)
- `--verbose` / `-v` — append the offending script value (`found: …`) to each failure message
- `--policy` / `-P` — run only matching policies (repeatable or comma-separated; matches policy IDs or feature stems; supports globs such as `GLCI-SHELL-PIN*`)

Tokens are only sent on `remote:` HTTP fetches when the remote URL host matches
`--gitlab-url` (or `CI_SERVER_URL` / `GITLAB_URL`). Arbitrary third-party remotes
are fetched without authentication.

Local includes are resolved on disk without a token. Nested `local:` includes
inside fetched `remote:` / `project:` YAML are resolved relative to that origin
(URL directory or same project/ref). When an include cannot be resolved,
`shell-check` prints an **Include coverage gap** warning and lists the entry in
markdown/HTML reports under **Coverage gaps**.

```bash
gitlab-compliance shell-check -p .gitlab-ci.yml \
  --include-nested \
  --resolve-external-includes \
  --token "$GITLAB_TOKEN" \
  --project "$CI_PROJECT_PATH"
```

GitLab CI example with external project includes:

```yaml
shell-check:
  image: python:3.12
  script:
    - pip install gitlab-compliance
    - gitlab-compliance shell-check -p .gitlab-ci.yml
        --resolve-external-includes
        --token "$GITLAB_TOKEN"
        --format markdown -o SHELL-CHECK.md
  artifacts:
    paths:
      - SHELL-CHECK.md
```

## Built-in Gherkin policies

Packaged scenarios live under `src/compliance/builtin_policies/shell/`:

| File | Focus |
| --- | --- |
| `shell-quoting.feature` | Variable and word splitting |
| `shell-error-handling.feature` | `set -e`, exit codes, traps |
| `shell-file-operations.feature` | Paths, redirects, temp files |
| `shell-command-substitution.feature` | `` ` `` and `$()` usage |
| `shell-conditionals.feature` | `if`/`test`/`[` patterns |
| `shell-pipelines.feature` | Pipes and pipeline exit status |
| `shell-security.feature` | Curl pipes, secrets, unsafe commands |
| `shell-portability.feature` | Bashisms and POSIX portability |
| `shell-ci-conventions.feature` | CI script hygiene |
| `shell-references.feature` | `!reference` resolution |
| `shell-pinning.feature` | Package manager and download pinning |

Pinning scenarios (`GLCI-SHELL-PIN-*`) include per-manager Gherkin, bad/good CI
snippets, and policy IDs in [Shell pinning examples](../../examples/shell-pinning.md).

## Custom policies

Write org-specific Gherkin using the same script steps, for example requiring
`--tags` on AWS CLI commands, then run:

```bash
gitlab-compliance check -f policies/ -p .gitlab-ci.yml
```

See [Shell check examples](../../examples/shell-check.md).

<!-- MANUAL DOCS:END -->



## Usage

```
Usage: gitlab-compliance shell-check [OPTIONS]
```

## Options
* `pipeline_file`:
  * Type: STRING
  * Default: `.gitlab-ci.yml`
  * Usage: `--pipeline
-p`

  Path to the GitLab CI pipeline YAML file.

* `output_format`:
  * Type: Choice(['console', 'markdown', 'html', 'mr-comment', 'codequality', 'junit'])
  * Default: `console`
  * Usage: `--format`

  Output format for the script validation report.

* `output_file`:
  * Type: STRING
  * Default: `none`
  * Usage: `--output-file
-o`

  Write rendered report to this file (markdown, html, mr-comment, junit).

* `include_nested`:
  * Type: BOOL
  * Default: `true`
  * Usage: `--include-nested`

  Resolve nested local include files into the compliance stash.

* `max_include_depth`:
  * Type: INT
  * Default: `none`
  * Usage: `--max-include-depth`

  Max local include nesting depth from the root file (omit for unlimited).

* `resolve_external_includes`:
  * Type: BOOL
  * Default: `none`
  * Usage: `--resolve-external-includes`

  Fetch remote and project include YAML (default: auto — remote always, project when a token is available).

* `gitlab_url`:
  * Type: STRING
  * Default: `none`
  * Usage: `--gitlab-url`

  GitLab instance URL (default: CI_SERVER_URL or https://gitlab.com).

* `token`:
  * Type: STRING
  * Default: `none`
  * Usage: `--token`

  GitLab API token (default: GITLAB_TOKEN or CI_JOB_TOKEN).

* `project`:
  * Type: STRING
  * Default: `none`
  * Usage: `--project`

  GitLab project path or ID for API-backed policy checks.

* `group`:
  * Type: STRING
  * Default: `none`
  * Usage: `--group`

  GitLab group path or ID for API-backed policy checks.

* `strict`:
  * Type: BOOL
  * Default: `false`
  * Usage: `--strict`

  Fail API-backed scenarios when connection info is missing (default: skip).

* `features_dir`:
  * Type: STRING
  * Default: `none`
  * Usage: `--features
-f`

  Policy directory to run instead of packaged shell standards. Defaults to packaged GLCI-SHELL policies.

* `help`:
  * Type: BOOL
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.


## CLI Help

```
Usage: gitlab-compliance shell-check [OPTIONS]

  Run packaged Gherkin shell standards for CI scripts (not the ShellCheck
  tool).

  Validates before_script/script/after_script using builtin GLCI-SHELL-*
  policies. Does not install, detect, or invoke the external ShellCheck
  binary.

Options:
  -p, --pipeline TEXT             Path to the GitLab CI pipeline YAML file.
  --format [console|markdown|html|mr-comment|codequality|junit]
                                  Output format for the script validation
                                  report.
  -o, --output-file TEXT          Write rendered report to this file
                                  (markdown, html, mr-comment, junit).
  --include-nested / --no-include-nested
                                  Resolve nested local include files into the
                                  compliance stash.
  --max-include-depth INTEGER     Max local include nesting depth from the
                                  root file (omit for unlimited).
  --resolve-external-includes / --no-resolve-external-includes
                                  Fetch remote and project include YAML
                                  (default: auto — remote always, project when
                                  a token is available).
  --gitlab-url TEXT               GitLab instance URL (default: CI_SERVER_URL
                                  or https://gitlab.com).
  --token TEXT                    GitLab API token (default: GITLAB_TOKEN or
                                  CI_JOB_TOKEN).
  --project TEXT                  GitLab project path or ID for API-backed
                                  policy checks.
  --group TEXT                    GitLab group path or ID for API-backed
                                  policy checks.
  --strict                        Fail API-backed scenarios when connection
                                  info is missing (default: skip).
  -f, --features TEXT             Policy directory to run instead of packaged
                                  shell standards. Defaults to packaged GLCI-
                                  SHELL policies.
  --help                          Show this message and exit.
```
