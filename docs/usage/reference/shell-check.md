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
- GitLab CI pinning (package managers below, checksums, docker image tags),
  CI hygiene, `!reference` resolution

Scripts are composed from `extends`, YAML anchors, and `!reference` before
scenarios run. Hidden jobs (names starting with `.`) are included.

## Supported package managers

Shell pinning policies (`GLCI-SHELL-PIN-*`) and unit tests cover these install
commands. Each package on a line must be version-pinned.

| Manager | Commands matched | Pinned example | Policy |
| --- | --- | --- | --- |
| apk | `apk add` | `apk add curl=8.5.0-r0` | `GLCI-SHELL-PIN-004` |
| apt / apt-get | `apt install`, `apt-get install` | `apt-get install curl=7.88.1-10` | `GLCI-SHELL-PIN-005` |
| yum / dnf / microdnf | `yum install`, `dnf install`, `microdnf install` | `dnf install curl-7.76.1-23.el9` | `GLCI-SHELL-PIN-010` |
| pip / pip3 | `pip install`, `pip3 install` | `pip3 install "requests==2.32.0"` | `GLCI-SHELL-PIN-003` |
| npm / yarn | `npm install -g`, `yarn global add` | `npm install -g cowsay@1.0.0` | `GLCI-SHELL-PIN-006` |
| go | `go install` | `go install example.com/cmd@v1.2.3` | `GLCI-SHELL-PIN-007` |

Related (not OS package managers): `docker run` / `docker pull` / `docker create`
must use an explicit tag or `sha256` digest (`GLCI-SHELL-PIN-009`).

Not covered yet: `zypper`, `pacman`, and similar tools outside the table above.

Gherkin scenarios, bad/good CI snippets, and policy IDs for each manager are in
[Shell pinning examples](../../examples/shell-pinning.md).

## Quick start

```bash
gitlab-compliance shell-check -p .gitlab-ci.yml
```

Markdown report:

```bash
gitlab-compliance shell-check -p .gitlab-ci.yml --format markdown -o SHELL-CHECK.md
```

Also available via `check --with-shell-check` (adds packaged `GLCI-SHELL-*`
policies alongside your `-f` directory). `--with-builtin` does **not** include
shell policies; add `--with-shell-check` explicitly when needed.

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
  * Type: Choice(['console', 'markdown', 'html', 'mr-comment', 'codequality'])
  * Default: `console`
  * Usage: `--format`

  Output format for the script validation report.

* `output_file`:
  * Type: STRING
  * Default: `none`
  * Usage: `--output-file
-o`

  Write rendered report to this file (markdown, html, mr-comment).

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
  --format [console|markdown|html|mr-comment|codequality]
                                  Output format for the script validation
                                  report.
  -o, --output-file TEXT          Write rendered report to this file
                                  (markdown, html, mr-comment).
  --include-nested / --no-include-nested
                                  Resolve nested local include files into the
                                  compliance stash.
  --max-include-depth INTEGER     Max local include nesting depth from the
                                  root file (omit for unlimited).
  -f, --features TEXT             Policy directory to run instead of packaged
                                  shell standards. Defaults to packaged GLCI-
                                  SHELL policies.
  --help                          Show this message and exit.
```
