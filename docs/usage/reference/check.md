# check

Run Gherkin compliance policies against GitLab CI YAML and optional API settings.

## Usage

```
Usage: gitlab-compliance check [OPTIONS]
```

## Options
* `features_dir` (REQUIRED):
  * Type: STRING
  * Default: `sentinel.unset`
  * Usage: `--features
-f`

  Directory containing compliance policy .feature files or an OCI reference (oci://registry.example.com/policies:1.0.0).

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

  Output format for the compliance report.

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

* `update`:
  * Type: BOOL
  * Default: `false`
  * Usage: `--update`

  Pull the latest policies from an OCI registry before running checks.

* `policy_cache_dir`:
  * Type: STRING
  * Default: `none`
  * Usage: `--policy-cache-dir`

  Directory used when pulling OCI policy bundles (default: system temp).

* `dry_run`:
  * Type: BOOL
  * Default: `false`
  * Usage: `--dry-run`

  Parse and list scenarios without asserting.

* `fix_supply_chain`:
  * Type: BOOL
  * Default: `false`
  * Usage: `--fix-supply-chain`

  Auto-fix outdated include refs and pin container images to sha256 digests.

* `fix_policies`:
  * Type: BOOL
  * Default: `false`
  * Usage: `--fix-policies`

  After an initial policy run, apply allowlisted BDD remediations (see docs/usage/fix-policies.md), then re-check.

* `create_mr`:
  * Type: BOOL
  * Default: `false`
  * Usage: `--create-mr`

  After --fix-supply-chain and/or --fix-policies, commit changed files and open a GitLab merge request (needs a project/personal access token; CI_JOB_TOKEN is usually insufficient; failures exit 2 after the report).

* `post_mr_comment`:
  * Type: BOOL
  * Default: `false`
  * Usage: `--post-mr-comment`

  Post the compliance mr-comment body to a GitLab merge request.

* `mr_iid`:
  * Type: INT
  * Default: `none`
  * Usage: `--mr-iid`

  Merge request IID for --post-mr-comment (default: CI_MERGE_REQUEST_IID).

* `mr_branch`:
  * Type: STRING
  * Default: `none`
  * Usage: `--mr-branch`

  Source branch for --create-mr (default: gitlab-compliance/supply-chain-fix). Reuses an open MR for this branch, or reopens the most recently updated closed one.

* `mr_target_branch`:
  * Type: STRING
  * Default: `none`
  * Usage: `--mr-target-branch`

  Target branch for --create-mr (default: project default branch).

* `mr_comment_file`:
  * Type: STRING
  * Default: `none`
  * Usage: `--mr-comment-file`

  Optional pre-rendered markdown file to post with --post-mr-comment.

* `with_builtin`:
  * Type: BOOL
  * Default: `false`
  * Usage: `--with-builtin`

  Also run bundled baseline policies shipped with gitlab-compliance.

* `help`:
  * Type: BOOL
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.


## CLI Help

```
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
  --max-include-depth INTEGER     Max local include nesting depth from the
                                  root file (omit for unlimited).
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
  --fix-supply-chain              Auto-fix outdated include refs and pin
                                  container images to sha256 digests.
  --fix-policies                  After an initial policy run, apply
                                  allowlisted BDD remediations (see
                                  docs/usage/fix-policies.md), then re-check.
  --create-mr                     After --fix-supply-chain and/or
                                  --fix-policies, commit changed files and
                                  open a GitLab merge request.
  --post-mr-comment               Post the compliance mr-comment body to a
                                  GitLab merge request.
  --mr-iid INTEGER                Merge request IID for --post-mr-comment
                                  (default: CI_MERGE_REQUEST_IID).
  --mr-branch TEXT                Source branch for --create-mr (default:
                                  gitlab-compliance/supply-chain-fix). Reuses
                                  an open MR for this branch, or reopens a
                                  closed one.
  --mr-target-branch TEXT         Target branch for --create-mr (default:
                                  project default branch).
  --mr-comment-file TEXT          Optional pre-rendered markdown file to post
                                  with --post-mr-comment.
  --with-builtin                  Also run bundled baseline policies shipped
                                  with gitlab-compliance.
  --help                          Show this message and exit.
```
