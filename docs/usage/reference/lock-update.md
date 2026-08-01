# lock update

Refresh `.gitlab-ci.lock` (alias for generate).

## Usage

```
Usage: gitlab-compliance lock update [OPTIONS]
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
  * Default: `none`
  * Usage: `--resolve-external-includes`

  Fetch remote and project include YAML (default: auto — remote always, project when a token is available).

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
  * Default: `false`
  * Usage: `--enrich`

  Resolve include release metadata and image digests via APIs (requires --token). Offline inventory is the default.

* `help`:
  * Type: BOOL
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.


## CLI Help

```
Usage: gitlab-compliance lock update [OPTIONS]

  Refresh `.gitlab-ci.lock` (alias for generate).

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
                                  Fetch remote and project include YAML
                                  (default: auto — remote always, project when
                                  a token is available).
  -f, --features TEXT             Optional policy directory to include in the
                                  inventory hash. When set, policy changes
                                  update the lock fingerprint.
  --gitlab-url TEXT               GitLab instance URL (default: CI_SERVER_URL
                                  or https://gitlab.com).
  --token TEXT                    GitLab API token (default: GITLAB_TOKEN or
                                  CI_JOB_TOKEN).
  --enrich / --no-enrich          Resolve include release metadata and image
                                  digests via APIs (requires --token). Offline
                                  inventory is the default.
  --help                          Show this message and exit.
```
