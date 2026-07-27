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
- GitLab CI pinning (`apk`/`pip`/checksums), CI hygiene, `!reference` resolution

Scripts are composed from `extends`, YAML anchors, and `!reference` before
scenarios run. Hidden jobs (names starting with `.`) are included.

## Quick start

```bash
gitlab-compliance shell-check -p .gitlab-ci.yml
```

Markdown report:

```bash
gitlab-compliance shell-check -p .gitlab-ci.yml --format markdown -o SHELL-CHECK.md
```

Also available via `check --with-builtin` (shell features ship alongside other
bundled policies).

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
