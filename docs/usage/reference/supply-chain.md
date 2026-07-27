# supply-chain

Run packaged supply-chain pinning policies against GitLab CI YAML.

    Validates include, image, and service version pinning using bundled
    GLCI-IMAGE-PINNING, GLCI-INCLUDE-VERSIONS, and related policies.

<!-- MANUAL DOCS:START -->

## What it checks

Bundled policies cover:

- **Include pinning** (`GLCI-INCLUDE-VERSIONS`)
- **Container image pinning** (`GLCI-IMAGE-PINNING`)
- **Service container pinning** (for example `docker:dind` version tags)

## Run

```bash
gitlab-compliance supply-chain -p .gitlab-ci.yml
```

Also available via `check --with-supply-chain` (read-only policy checks; not the
same as `check --fix-supply-chain`, which mutates YAML). Omit `-f` to run only
the bundled pack, or pass `-f` to merge your policies alongside it.

For auto-remediation of outdated includes and unpinned images, use
[`check --fix-supply-chain`](check.md#fix-supply-chain).

See [Image pinning](../../examples/image-pinning.md) and
[Include versions](../../examples/include-versions.md).

<!-- MANUAL DOCS:END -->



## Usage

```
Usage: gitlab-compliance supply-chain [OPTIONS]
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

  Output format for the supply-chain compliance report.

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

  Policy directory to run instead of packaged supply-chain policies. Defaults to bundled include, image, and service pinning.

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

* `help`:
  * Type: BOOL
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.


## CLI Help

```
Usage: gitlab-compliance supply-chain [OPTIONS]

  Run packaged supply-chain pinning policies against GitLab CI YAML.

  Validates include, image, and service version pinning using bundled GLCI-
  IMAGE-PINNING, GLCI-INCLUDE-VERSIONS, and related policies.

Options:
  -p, --pipeline TEXT             Path to the GitLab CI pipeline YAML file.
  --format [console|markdown|html|mr-comment|codequality]
                                  Output format for the supply-chain
                                  compliance report.
  -o, --output-file TEXT          Write rendered report to this file
                                  (markdown, html, mr-comment).
  --include-nested / --no-include-nested
                                  Resolve nested local include files into the
                                  compliance stash.
  --max-include-depth INTEGER     Max local include nesting depth from the
                                  root file (omit for unlimited).
  -f, --features TEXT             Policy directory to run instead of packaged
                                  supply-chain policies. Defaults to bundled
                                  include, image, and service pinning.
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
  --help                          Show this message and exit.
```
