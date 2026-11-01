# lock fingerprint

Print the inventory fingerprint (for CI skip / cache keys).

## Usage

```
Usage: gitlab-compliance lock fingerprint [OPTIONS]
```

## Options
* `pipeline_file`:
  * Type: STRING
  * Default: `.gitlab-ci.yml`
  * Usage: `--pipeline
-p`

  Path to the GitLab CI pipeline YAML file.

* `lock_file`:
  * Type: STRING
  * Default: `.gitlab-ci.lock`
  * Usage: `--lock-file
-l`

  Path to the `.gitlab-ci.lock` inventory file.

* `include_nested`:
  * Type: BOOL
  * Default: `true`
  * Usage: `--include-nested`

  Resolve nested local include files into the inventory.

* `max_include_depth`:
  * Type: INT
  * Default: `none`
  * Usage: `--max-include-depth`

  Max local include nesting depth from the root file (omit for unlimited).

* `resolve_external_includes`:
  * Type: BOOL
  * Default: `true`
  * Usage: `--resolve-external-includes`

  Fetch the full upstream include closure (remote/project YAML; templates follow --resolve-templates). Default: enabled.

* `resolve_templates`:
  * Type: BOOL
  * Default: `true`
  * Usage: `--resolve-templates`

  Fetch GitLab CI template includes into the inventory closure. Ignored when --no-resolve-external-includes is set.

* `features_dir`:
  * Type: STRING
  * Default: `none`
  * Usage: `--features
-f`

  Optional policy directory to include in the inventory hash. When set, policy changes update the lock fingerprint.

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

* `enrich`:
  * Type: BOOL
  * Default: `true`
  * Usage: `--enrich`

  Attempt image digest resolution (Docker Hub without a token; GitLab Container Registry with --token) and include release metadata when a token is available. Use --no-enrich for offline.

* `verbose`:
  * Type: BOOL
  * Default: `false`
  * Usage: `--verbose
-v`

  Show full inventory tables (no row truncation).

* `quiet`:
  * Type: BOOL
  * Default: `false`
  * Usage: `--quiet
-q`

  Minimal output (fingerprint only) for scripts and CI.

* `as_json`:
  * Type: BOOL
  * Default: `false`
  * Usage: `--json`

  Emit a machine-readable JSON report instead of the Rich UI.

* `dotenv_file`:
  * Type: STRING
  * Default: `none`
  * Usage: `--dotenv`

  Write a GitLab dotenv report with GITLAB_COMPLIANCE_LOCK_FINGERPRINT (for cache keys / child-pipeline rules).

* `from_lock`:
  * Type: BOOL
  * Default: `false`
  * Usage: `--from-lock`

  Read fingerprint from the lock file instead of recomputing from YAML.

* `help`:
  * Type: BOOL
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.


## CLI Help

```
Usage: gitlab-compliance lock fingerprint [OPTIONS]

  Print the inventory fingerprint (for CI skip / cache keys).

Options:
  -p, --pipeline TEXT             Path to the GitLab CI pipeline YAML file.
                                  [default: .gitlab-ci.yml]
  -l, --lock-file TEXT            Path to the `.gitlab-ci.lock` inventory
                                  file.  [default: .gitlab-ci.lock]
  --include-nested / --no-include-nested
                                  Resolve nested local include files into the
                                  inventory.
  --max-include-depth INTEGER     Max local include nesting depth from the
                                  root file (omit for unlimited).
  --resolve-external-includes / --no-resolve-external-includes
                                  Fetch the full upstream include closure
                                  (remote/project YAML; templates follow
                                  --resolve-templates). Default: enabled.
  --resolve-templates / --no-resolve-templates
                                  Fetch GitLab CI template includes into the
                                  inventory closure. Ignored when --no-
                                  resolve-external-includes is set.
  -f, --features TEXT             Optional policy directory to include in the
                                  inventory hash. When set, policy changes
                                  update the lock fingerprint.
  --gitlab-url TEXT               GitLab instance URL (default: CI_SERVER_URL
                                  or https://gitlab.com).
  --token TEXT                    GitLab API token (default: GITLAB_TOKEN or
                                  CI_JOB_TOKEN).
  --enrich / --no-enrich          Attempt image digest resolution (Docker Hub
                                  without a token; GitLab Container Registry
                                  with --token) and include release metadata
                                  when a token is available. Use --no-enrich
                                  for offline.
  -v, --verbose                   Show full inventory tables (no row
                                  truncation).
  -q, --quiet                     Minimal output (fingerprint only) for
                                  scripts and CI.
  --json                          Emit a machine-readable JSON report instead
                                  of the Rich UI.
  --dotenv TEXT                   Write a GitLab dotenv report with
                                  GITLAB_COMPLIANCE_LOCK_FINGERPRINT (for
                                  cache keys / child-pipeline rules).
  --from-lock / --from-pipeline   Read fingerprint from the lock file instead
                                  of recomputing from YAML.
  --help                          Show this message and exit.
```
