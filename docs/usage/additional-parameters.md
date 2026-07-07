# Additional Parameters

Options beyond the core `-f` and `-p` flags on `gitlab-compliance compliance`.

## `--include-nested` / `--no-include-nested`

**Default:** nested local includes are resolved.

When enabled, `include:` entries that reference local project files are merged into the compliance entity stash so policies can see jobs and variables from included fragments.

```bash
gitlab-compliance compliance -f policies/ -p .gitlab-ci.yml --no-include-nested
```

## `--strict`

**Default:** off (API scenarios skip when token or project/group is missing).

When enabled, API-backed `Given` steps fail instead of skipping if `GITLAB_TOKEN` / `CI_JOB_TOKEN` and `--project` or `--group` are not available.

```bash
gitlab-compliance compliance -f policies/ -p .gitlab-ci.yml --strict
```

Use `--strict` in CI jobs that must enforce API checks.

## `--dry-run`

Parse scenarios and list them without running assertions.

```bash
gitlab-compliance compliance -f policies/ -p .gitlab-ci.yml --dry-run
```

## `--fix`

Auto-remediate supply-chain issues before running policies:

- **Project/component includes** — bump `ref:` or `@version` to the latest semver tag from GitLab
- **Container images** — rewrite `image:` / `services:` to `@sha256:<digest>` for the resolved tag

Requires a GitLab token (`--token`, `GITLAB_TOKEN`, or `CI_JOB_TOKEN`). Cannot be combined with `--dry-run`.

```bash
gitlab-compliance compliance -f policies/security/ -p .gitlab-ci.yml --fix
```

## `--update`

With an OCI `-f` reference, pull the latest policy bundle before executing checks.

```bash
gitlab-compliance compliance -f oci://registry.example.com/org/policies:1.0.0 -p .gitlab-ci.yml --update
```

## `--policy-cache-dir`

Directory used when extracting OCI policy bundles (default: system temp directory).

```bash
gitlab-compliance compliance -f oci://registry.example.com/org/policies:1.0.0 \
  -p .gitlab-ci.yml --policy-cache-dir /tmp/policy-cache
```

## `--gitlab-url`

GitLab instance URL for API checks. Defaults to `CI_SERVER_URL` or `https://gitlab.com`.

```bash
gitlab-compliance compliance -f policies/ -p .gitlab-ci.yml \
  --gitlab-url https://gitlab.example.com --project my-group/my-project
```

## Documentation commands

### `generate`

| Option | Description |
|--------|-------------|
| `-i` / `--input-config` | Pipeline YAML path (default: `.gitlab-ci.yml`) |
| `-o` / `--output-file` | Output path |
| `--format` | `markdown` (default) or `html` |
| `--detailed` | Include workflow and per-job `rules` |
| `--dry-mode` | Print to stdout without writing a file |

### `compliance-doc`

| Option | Description |
|--------|-------------|
| `-f` / `--features` | Policy directory |
| `--format` | `markdown` (default) or `html` |
| `-o` / `--output-file` | Catalog output path |

### `compliance-push` / `compliance-pull`

```bash
gitlab-compliance compliance-push -f policies/ registry.example.com/org/policies:1.0.0
gitlab-compliance compliance-pull oci://registry.example.com/org/policies:1.0.0 -o policies/
```

Full generated reference: [Command Reference](command-reference.md).
