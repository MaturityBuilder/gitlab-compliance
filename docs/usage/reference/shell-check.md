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

## Built-in Gherkin policies

Packaged scenarios from `src/compliance/builtin_policies/shell/`. Every scenario
starts from `Given I have any job with effective script defined` unless noted.

### Quoting (`GLCI-SHELL-QUOTE`)

```gherkin
Scenario: Variables are quoted when expanded
  # GLCI-SHELL-QUOTE-001
  Given I have any job with effective script defined
  When a variable is expanded within a command
  Then the variable must be wrapped in double quotes

Scenario: Variables used in paths are quoted
  # GLCI-SHELL-QUOTE-002
  Given I have any job with effective script defined
  When variables are used as part of a path
  Then all variables must be safely quoted

Scenario: Command substitutions are quoted
  # GLCI-SHELL-QUOTE-003
  Given I have any job with effective script defined
  When command substitution is used
  Then the result must be quoted unless word splitting is intended

Scenario: Arrays are expanded correctly
  # GLCI-SHELL-QUOTE-004
  Given I have any job with effective script defined
  When an array is expanded
  Then array "@" syntax must be used where appropriate
```

### Error handling (`GLCI-SHELL-ERR`)

```gherkin
Scenario: Multi-line scripts use strict mode
  # GLCI-SHELL-ERR-001
  Given I have any job with effective script defined
  When the effective script has more than 1 line
  Then the script must enable strict mode options

Scenario: Commands return meaningful exit codes
  # GLCI-SHELL-ERR-002
  Given I have any job with effective script defined
  Then failure must be handled explicitly

Scenario: Functions propagate failures
  # GLCI-SHELL-ERR-003
  Given I have any job with effective script defined
  Then functions must propagate failures
```

### File operations (`GLCI-SHELL-FILE`)

```gherkin
Scenario: File paths are quoted
  # GLCI-SHELL-FILE-001
  Given I have any job with effective script defined
  Then file paths must be quoted

Scenario: Temporary files are securely created
  # GLCI-SHELL-FILE-002
  Given I have any job with effective script defined
  When temporary files are required
  Then mktemp must be used for temporary files

Scenario: Dangerous rm operations are protected
  # GLCI-SHELL-FILE-003
  Given I have any job with effective script defined
  When rm is used recursively
  Then path validation must be performed for recursive rm
```

### Command substitution (`GLCI-SHELL-SUB`)

```gherkin
Scenario: Legacy backticks are not used
  # GLCI-SHELL-SUB-001
  Given I have any job with effective script defined
  Then command substitution must use dollar parentheses

Scenario: Nested command substitution is readable
  # GLCI-SHELL-SUB-002
  Given I have any job with effective script defined
  Then nested command substitution must use dollar parentheses
```

### Conditionals (`GLCI-SHELL-TEST`)

```gherkin
Scenario: Test operators are portable
  # GLCI-SHELL-TEST-001
  Given I have any job with effective script defined
  Then POSIX compliant operators must be used

Scenario: Variables are quoted in test statements
  # GLCI-SHELL-TEST-002
  Given I have any job with effective script defined
  Then variables in test expressions must be quoted
```

### Pipelines (`GLCI-SHELL-PIPE`)

```gherkin
Scenario: Pipeline failures are detected
  # GLCI-SHELL-PIPE-001
  Given I have any job with effective script defined
  When a pipeline is used
  Then pipefail must be enabled

Scenario: Exit codes are checked across pipelines
  # GLCI-SHELL-PIPE-002
  Given I have any job with effective script defined
  When a pipeline is used
  Then pipefail must be enabled
```

### Security (`GLCI-SHELL-SAFE`)

```gherkin
Scenario: Eval is not used
  # GLCI-SHELL-SAFE-001
  Given I have any job with effective script defined
  Then eval must not be used

Scenario: Untrusted input is not executed
  # GLCI-SHELL-SAFE-002
  Given I have any job with effective script defined
  Then untrusted remote scripts must not be executed

Scenario: User input is sanitised
  # GLCI-SHELL-SAFE-003
  Given I have any job with effective script defined
  Then user supplied variables must be quoted or validated

Scenario: Hardcoded secrets are not present
  # GLCI-SHELL-SAFE-004
  Given I have any job with effective script defined
  Then hardcoded secrets must not be present

Scenario: chmod 777 is not used
  # GLCI-SHELL-SAFE-005
  Given I have any job with effective script defined
  Then chmod 777 must not be used
```

### Portability (`GLCI-SHELL-PORT`)

```gherkin
Scenario: Shebang is valid when present
  # GLCI-SHELL-PORT-001
  Given I have any job with effective script defined
  Then shebang must be valid when present

Scenario: Bash specific features are declared
  # GLCI-SHELL-PORT-002
  Given I have any job with effective script defined
  Then bash specific features must declare bash

Scenario: POSIX compatibility is maintained for sh
  # GLCI-SHELL-PORT-003
  Given I have any job with effective script defined
  Then POSIX shebang scripts must not use bashisms
```

### CI conventions (`GLCI-SHELL-CI`)

```gherkin
Scenario: curl must use fail flag
  # GLCI-SHELL-CI-001
  Given I have any job with effective script defined
  Then curl must use fail flag

Scenario: Deprecated CI_BUILD variables must not be used
  # GLCI-SHELL-CI-002
  Given I have any job with effective script defined
  Then deprecated CI_BUILD variables must not be used

Scenario: CI variables should be quoted
  # GLCI-SHELL-CI-003
  Given I have any job with effective script defined
  Then user supplied variables must be quoted or validated
```

### Script references (`GLCI-SHELL-REF`)

```gherkin
Scenario: Scripts must not contain unresolved references
  # GLCI-SHELL-REF-001
  Given I have any job with effective script defined
  Then unresolved script references must not be present
```

### Dependency pinning (`GLCI-SHELL-PIN`)

```gherkin
Scenario: Script downloads must verify checksums
  # GLCI-SHELL-PIN-001
  Then script downloads must verify checksums

Scenario: Scripts must not pipe remote downloads to a shell
  # GLCI-SHELL-PIN-002
  Then untrusted remote scripts must not be executed

Scenario: pip install must pin package versions
  # GLCI-SHELL-PIN-003
  Then package installs of type "pip" must use pinned versions

Scenario: apk add must pin package versions
  # GLCI-SHELL-PIN-004
  Then package installs of type "apk" must use pinned versions

Scenario: apt-get install must pin package versions
  # GLCI-SHELL-PIN-005
  Then package installs of type "apt" must use pinned versions

Scenario: npm global installs must pin package versions
  # GLCI-SHELL-PIN-006
  Then package installs of type "npm" must use pinned versions

Scenario: go install must pin module versions
  # GLCI-SHELL-PIN-007
  Then package installs of type "go" must use pinned versions

Scenario: git clone must verify commit or tag
  # GLCI-SHELL-PIN-008
  Then git clone must verify commit or tag

Scenario: docker run and pull must pin container images
  # GLCI-SHELL-PIN-009
  Then docker commands must pin container images to a tag or sha256 digest

Scenario: yum and dnf install must pin package versions
  # GLCI-SHELL-PIN-010
  Then package installs of type "yum" must use pinned versions
```

Bad/good CI examples for each package manager:
[Shell pinning](../../examples/shell-pinning.md).

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
