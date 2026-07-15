# check

Run Gherkin compliance policies against GitLab CI YAML and optional API settings.

## Usage

```text
Usage: gitlab-compliance check [OPTIONS]
```

## Options

* `features_dir` (REQUIRED):
  * Type: `STRING`
  * Default: _required_
  * Usage: `--features, -f`

  Directory containing compliance policy .feature files or an OCI reference (oci://registry.example.com/policies:1.0.0).

* `pipeline_file`:
  * Type: `STRING`
  * Default: `.gitlab-ci.yml`
  * Usage: `--pipeline, -p`

  Path to the GitLab CI pipeline YAML file.

* `output_format`:
  * Type: `Choice(['console', 'markdown', 'html', 'mr-comment', 'codequality'])`
  * Default: `console`
  * Usage: `--format`

  Output format for the compliance report.

* `output_file`:
  * Type: `STRING`
  * Default: `none`
  * Usage: `--output-file, -o`

  Write rendered report to this file (markdown, html, mr-comment).

* `include_nested`:
  * Type: `BOOL`
  * Default: `true`
  * Usage: `--include-nested`

  Resolve nested local include files into the compliance stash.

* `gitlab_url`:
  * Type: `STRING`
  * Default: `none`
  * Usage: `--gitlab-url`

  GitLab instance URL (default: CI_SERVER_URL or https://gitlab.com).

* `token`:
  * Type: `STRING`
  * Default: `none`
  * Usage: `--token`

  GitLab API token (default: GITLAB_TOKEN or CI_JOB_TOKEN).

* `project`:
  * Type: `STRING`
  * Default: `none`
  * Usage: `--project`

  GitLab project path or ID for API-backed policy checks.

* `group`:
  * Type: `STRING`
  * Default: `none`
  * Usage: `--group`

  GitLab group path or ID for API-backed policy checks.

* `strict`:
  * Type: `BOOL`
  * Default: `false`
  * Usage: `--strict`

  Fail API-backed scenarios when connection info is missing (default: skip).

* `update`:
  * Type: `BOOL`
  * Default: `false`
  * Usage: `--update`

  Pull the latest policies from an OCI registry before running checks.

* `policy_cache_dir`:
  * Type: `STRING`
  * Default: `none`
  * Usage: `--policy-cache-dir`

  Directory used when pulling OCI policy bundles (default: system temp).

* `dry_run`:
  * Type: `BOOL`
  * Default: `false`
  * Usage: `--dry-run`

  Parse and list scenarios without asserting.

* `fix`:
  * Type: `BOOL`
  * Default: `false`
  * Usage: `--fix`

  Auto-fix outdated include refs and pin container images to sha256 digests.

* `with_builtin`:
  * Type: `BOOL`
  * Default: `false`
  * Usage: `--with-builtin`

  Also run bundled baseline policies shipped with gitlab-compliance.

* `help`:
  * Type: `BOOL`
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.


## CLI Help

```text
Usage: gitlab-compliance check [OPTIONS]

  Run Gherkin compliance policies against GitLab CI YAML and optional API
  settings.

Options:
  -f, --features TEXT             Directory containing compliance policy
                                  .feature files or an OCI reference
                                  (oci://registry.example.com/policies:1.0.0).
                                  [required]
  -p, --pipeline TEXT             Path to the GitLab CI pipeline YAML file.
  --format [console|markdown|html|mr-comment|codequality]
                                  Output format for the compliance report.
  -o, --output-file TEXT          Write rendered report to this file
                                  (markdown, html, mr-comment).
  --include-nested / --no-include-nested
                                  Resolve nested local include files into the
                                  compliance stash.
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
  --update                        Pull the latest policies from an OCI
                                  registry before running checks.
  --policy-cache-dir TEXT         Directory used when pulling OCI policy
                                  bundles (default: system temp).
  --dry-run                       Parse and list scenarios without asserting.
  --fix                           Auto-fix outdated include refs and pin
                                  container images to sha256 digests.
  --with-builtin                  Also run bundled baseline policies shipped
                                  with gitlab-compliance.
  --help                          Show this message and exit.
```
