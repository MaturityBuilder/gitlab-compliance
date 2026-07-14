# check

Run Gherkin compliance policies against GitLab CI YAML and optional API settings.

## Usage

```text
Usage: gitlab-compliance check [OPTIONS]
```

## Options

| Name | Type | Required | Default | Usage | Description |
| ---- | ---- | -------- | ------- | ----- | ----------- |
| `features_dir` | text | yes | _not set_ | `--features, -f` | Directory containing compliance policy .feature files or an OCI reference (oci://registry.example.com/policies:1.0.0). |
| `pipeline_file` | text | no | `.gitlab-ci.yml` | `--pipeline, -p` | Path to the GitLab CI pipeline YAML file. |
| `output_format` | choice: `console`, `markdown`, `html`, `mr-comment`, `codequality` | no | `console` | `--format` | Output format for the compliance report. |
| `output_file` | text | no | `none` | `--output-file, -o` | Write rendered report to this file (markdown, html, mr-comment). |
| `include_nested` | boolean | no | `true` | `--include-nested, --no-include-nested` | Resolve nested local include files into the compliance stash. |
| `gitlab_url` | text | no | `none` | `--gitlab-url` | GitLab instance URL (default: CI_SERVER_URL or https://gitlab.com). |
| `token` | text | no | `none` | `--token` | GitLab API token (default: GITLAB_TOKEN or CI_JOB_TOKEN). |
| `project` | text | no | `none` | `--project` | GitLab project path or ID for API-backed policy checks. |
| `group` | text | no | `none` | `--group` | GitLab group path or ID for API-backed policy checks. |
| `strict` | boolean | no | `false` | `--strict` | Fail API-backed scenarios when connection info is missing (default: skip). |
| `update` | boolean | no | `false` | `--update` | Pull the latest policies from an OCI registry before running checks. |
| `policy_cache_dir` | text | no | `none` | `--policy-cache-dir` | Directory used when pulling OCI policy bundles (default: system temp). |
| `dry_run` | boolean | no | `false` | `--dry-run` | Parse and list scenarios without asserting. |
| `fix` | boolean | no | `false` | `--fix` | Auto-fix outdated include refs and pin container images to sha256 digests. |
| `with_builtin` | boolean | no | `false` | `--with-builtin` | Also run bundled baseline policies shipped with gitlab-compliance. |
| `help` | boolean | no | `false` | `--help` | Show this message and exit. |

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
