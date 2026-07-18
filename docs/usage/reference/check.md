# check

Run Gherkin compliance policies against GitLab CI YAML and optional API settings.

## Usage

```text
Usage: gitlab-compliance check [OPTIONS]
```

## Options

### `--features, -f`

- **Name:** `features_dir`
- **Kind:** Option
- **Required:** yes
- **Default:** `required`
- **Type:** `STRING`
- **Description:** Directory containing compliance policy .feature files or an OCI reference (oci://registry.example.com/policies:1.0.0).

### `--pipeline, -p`

- **Name:** `pipeline_file`
- **Kind:** Option
- **Required:** no
- **Default:** `.gitlab-ci.yml`
- **Type:** `STRING`
- **Description:** Path to the GitLab CI pipeline YAML file.

### `--format`

- **Name:** `output_format`
- **Kind:** Option
- **Required:** no
- **Default:** `console`
- **Type:** `Choice(['console', 'markdown', 'html', 'mr-comment', 'codequality'])`
- **Description:** Output format for the compliance report.

### `--output-file, -o`

- **Name:** `output_file`
- **Kind:** Option
- **Required:** no
- **Default:** `not set`
- **Type:** `STRING`
- **Description:** Write rendered report to this file (markdown, html, mr-comment).

### `--include-nested, --no-include-nested`

- **Name:** `include_nested`
- **Kind:** Option
- **Required:** no
- **Default:** `true`
- **Type:** `BOOL`
- **Description:** Resolve nested local include files into the compliance stash.

### `--gitlab-url`

- **Name:** `gitlab_url`
- **Kind:** Option
- **Required:** no
- **Default:** `not set`
- **Type:** `STRING`
- **Description:** GitLab instance URL (default: CI_SERVER_URL or https://gitlab.com).

### `--token`

- **Name:** `token`
- **Kind:** Option
- **Required:** no
- **Default:** `not set`
- **Type:** `STRING`
- **Description:** GitLab API token (default: GITLAB_TOKEN or CI_JOB_TOKEN).

### `--project`

- **Name:** `project`
- **Kind:** Option
- **Required:** no
- **Default:** `not set`
- **Type:** `STRING`
- **Description:** GitLab project path or ID for API-backed policy checks.

### `--group`

- **Name:** `group`
- **Kind:** Option
- **Required:** no
- **Default:** `not set`
- **Type:** `STRING`
- **Description:** GitLab group path or ID for API-backed policy checks.

### `--strict`

- **Name:** `strict`
- **Kind:** Option
- **Required:** no
- **Default:** `false`
- **Type:** `BOOL`
- **Description:** Fail API-backed scenarios when connection info is missing (default: skip).

### `--update`

- **Name:** `update`
- **Kind:** Option
- **Required:** no
- **Default:** `false`
- **Type:** `BOOL`
- **Description:** Pull the latest policies from an OCI registry before running checks.

### `--policy-cache-dir`

- **Name:** `policy_cache_dir`
- **Kind:** Option
- **Required:** no
- **Default:** `not set`
- **Type:** `STRING`
- **Description:** Directory used when pulling OCI policy bundles (default: system temp).

### `--dry-run`

- **Name:** `dry_run`
- **Kind:** Option
- **Required:** no
- **Default:** `false`
- **Type:** `BOOL`
- **Description:** Parse and list scenarios without asserting.

### `--fix`

- **Name:** `fix`
- **Kind:** Option
- **Required:** no
- **Default:** `false`
- **Type:** `BOOL`
- **Description:** Auto-fix outdated include refs and pin container images to sha256 digests.

### `--with-builtin`

- **Name:** `with_builtin`
- **Kind:** Option
- **Required:** no
- **Default:** `false`
- **Type:** `BOOL`
- **Description:** Also run bundled baseline policies shipped with gitlab-compliance.


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
