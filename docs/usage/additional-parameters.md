# Additional Parameters

Options beyond the core `-f` and `-p` flags on `gitlab-compliance check`.

## `--include-nested` / `--no-include-nested`

**Default:** nested local includes are resolved.

When enabled, `include:` entries that reference local project files are merged
into the compliance entity stash so policies can see jobs and variables from
included fragments.

```bash
gitlab-compliance check -f policies/ -p .gitlab-ci.yml --no-include-nested
```

## `--max-include-depth`

**Default:** unlimited (omit the flag).

Limits how many local-include hops are followed from the root pipeline file when
nesting is enabled. Depth `0` is the root file; depth `1` is files included
directly by the root.

```bash
gitlab-compliance check -f policies/ -p .gitlab-ci.yml --max-include-depth 2
```

Also available on `generate` and `document gitstrings`.

## `--strict`

**Default:** off (API scenarios skip when token or project/group is missing).

When enabled, API-backed `Given` steps fail instead of skipping if
`GITLAB_TOKEN` / `CI_JOB_TOKEN` and `--project` or `--group` are not available.

```bash
gitlab-compliance check -f policies/ -p .gitlab-ci.yml --strict
```

Use `--strict` in CI jobs that must enforce API checks.

## `--dry-run`

Parse scenarios and list them without running assertions.

```bash
gitlab-compliance check -f policies/ -p .gitlab-ci.yml --dry-run
```

## `--fix`

Auto-remediate supply-chain issues before running policies:

- **Project/component includes** — bump `ref:` or `@version` to the latest
  semver tag from GitLab
- **Container images** — rewrite `image:` / `services:` to `@sha256:<digest>`
  for the resolved tag

Requires a GitLab token (`--token`, `GITLAB_TOKEN`, or `CI_JOB_TOKEN`). Cannot
be combined with `--dry-run`.

```bash
gitlab-compliance check -f policies/security/ -p .gitlab-ci.yml --fix
```

## `--create-mr`

After `--fix` rewrites local YAML, commit the changed files and open a GitLab
merge request. Requires `--fix`, a token, and `--project` (or
`CI_PROJECT_PATH`).

Optional: `--mr-branch`, `--mr-target-branch`.

```bash
gitlab-compliance check -f policies/security/ -p .gitlab-ci.yml \
  --fix --create-mr --project "$CI_PROJECT_PATH"
```

## `--post-mr-comment`

Post the compliance report as a note on an existing merge request. Uses
`--mr-iid` or `CI_MERGE_REQUEST_IID`. Optional `--mr-comment-file` posts a
pre-rendered body instead of regenerating from the run.

```bash
gitlab-compliance check -f policies/security/ -p .gitlab-ci.yml \
  --post-mr-comment --project "$CI_PROJECT_PATH"
```

## `--update`

With an OCI `-f` reference, pull the latest policy bundle before executing
checks.

```bash
gitlab-compliance check -f oci://registry.example.com/org/policies:1.0.0 -p
.gitlab-ci.yml --update
```

## `--policy-cache-dir`

Directory used when extracting OCI policy bundles (default: system temp
directory).

```bash
gitlab-compliance check -f oci://registry.example.com/org/policies:1.0.0 \
  -p .gitlab-ci.yml --policy-cache-dir /tmp/policy-cache
```

## `--gitlab-url`

GitLab instance URL for API checks. Defaults to `CI_SERVER_URL` or
`https://gitlab.com`.

```bash
gitlab-compliance check -f policies/ -p .gitlab-ci.yml \
  --gitlab-url https://gitlab.example.com --project my-group/my-project
```

## Documentation commands

### `generate`

| Option                  | Description                                    |
| ----------------------- | ---------------------------------------------- |
| `-i` / `--input-config` | Pipeline YAML path (default: `.gitlab-ci.yml`) |
| `-o` / `--output-file`  | Output path                                    |
| `--format`              | `markdown`, `swagger-markdown`, or `html`      |
| `--detailed`            | Include workflow and per-job `rules`           |
| `--dry-mode`            | Print to stdout without writing a file         |
| `-x` / `--exclude`      | Comma-separated sections or job attributes to omit (sections: `inputs`, `variables`, `includes`, `workflow`, `jobs`, `container_images`) |
| `-g` / `--group-by`     | Group jobs in the Jobs section by a job attribute (e.g. `stage`) |
| `--max-include-depth`   | Max local include nesting depth (omit for unlimited) |

Use `get-attributes` when you need an **include whitelist** of specific job
attributes as a table; use `generate --exclude` for a **blacklist** when
building full pipeline documentation.

Example:

```bash
gitlab-compliance generate -i .gitlab-ci.yml \
  --exclude variables,workflow,image \
  --group-by stage \
  --format swagger-markdown
```

### `policies doc`

| Option                 | Description                    |
| ---------------------- | ------------------------------ |
| `-f` / `--features`    | Policy directory               |
| `--format`             | `markdown` (default) or `html` |
| `-o` / `--output-file` | Catalog output path            |

### `policies push` / `policies pull`

```bash
gitlab-compliance policies push -f policies/
registry.example.com/org/policies:1.0.0
gitlab-compliance policies pull oci://registry.example.com/org/policies:1.0.0 -o
policies/
```
