# check

Run Gherkin compliance policies against GitLab CI YAML and optional API settings.

## Usage

```text
Usage: gitlab-compliance check [OPTIONS]
```

## Options

| Option | Type | Default | Description |
| ------ | ---- | ------- | ----------- |
| `--features, -f` | STRING | `required` | Directory containing compliance policy .feature files or an OCI reference (oci://registry.example.com/policies:1.0.0). |
| `--pipeline, -p` | STRING | `.gitlab-ci.yml` | Path to the GitLab CI pipeline YAML file. |
| `--format` | console, markdown, html, mr-comment, codequality | `console` | Output format for the compliance report. |
| `--output-file, -o` | STRING | `none` | Write rendered report to this file (markdown, html, mr-comment). |
| `--include-nested, --no-include-nested` | BOOL | `true` | Resolve nested local include files into the compliance stash. |
| `--gitlab-url` | STRING | `none` | GitLab instance URL (default: CI_SERVER_URL or GitLab.com). |
| `--token` | STRING | `none` | GitLab API token (default: GITLAB_TOKEN or CI_JOB_TOKEN). |
| `--project` | STRING | `none` | GitLab project path or ID for API-backed policy checks. |
| `--group` | STRING | `none` | GitLab group path or ID for API-backed policy checks. |
| `--strict` | BOOL | `false` | Fail API-backed scenarios when connection info is missing (default: skip). |
| `--update` | BOOL | `false` | Pull the latest policies from an OCI registry before running checks. |
| `--policy-cache-dir` | STRING | `none` | Directory used when pulling OCI policy bundles (default: system temp). |
| `--dry-run` | BOOL | `false` | Parse and list scenarios without asserting. |
| `--fix` | BOOL | `false` | Auto-fix outdated include refs and pin container images to sha256 digests. |
| `--with-builtin` | BOOL | `false` | Also run bundled baseline policies shipped with gitlab-compliance. |
| `--help` | BOOL | `false` | Show this message and exit. |


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
                                  or GitLab.com).
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
