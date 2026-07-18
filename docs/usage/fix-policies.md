# Auto-fix policies (`--fix-policies`)

`--fix-policies` remediates **failed** BDD scenarios only when they match an
explicit allowlist. Unsupported failures are left unchanged and reported as not
auto-fixable.

This is separate from [`--fix-supply-chain`](additional-parameters.md), which
rewrites includes/images before policies run.

## Usage

```bash
gitlab-compliance check -f policies/security/ -p .gitlab-ci.yml \
  --fix-policies --token "$GITLAB_TOKEN"
```

With an MR:

```bash
gitlab-compliance check -f policies/security/ -p .gitlab-ci.yml \
  --fix-policies --create-mr --project "$CI_PROJECT_PATH"
```

Both fix modes can be combined:

```bash
gitlab-compliance check -f policies/security/ -p .gitlab-ci.yml \
  --fix-supply-chain --fix-policies --create-mr --project "$CI_PROJECT_PATH"
```

Requires a GitLab token. Cannot be combined with `--dry-run`.

## Flow

1. Optional `--fix-supply-chain` rewrites.
2. Initial policy run.
3. Allowlisted failed scenarios → YAML remediations.
4. Optional `--create-mr` commits those edits.
5. Policies re-run; the final report reflects post-fix status.

## Supported remediations

| Policy ID | What it fixes |
| --- | --- |
| `GLCI-INCLUDE-VERSIONS-003` | Bump include `ref:` / `@version` to latest semver |
| `GLCI-INCLUDE-VERSIONS-004` | Same (adoption-window / age policies) |
| `GLCI-INCLUDE-VERSIONS-005` | Same |
| `GLCI-INCLUDE-VERSIONS-006` | Same (latest-N tags window) |
| `GLCI-IMAGE-PINNING-001` | Pin job/service images to `@sha256:<digest>` |

These IDs match the example policies under
`examples/example-policies/security/`.

## Not auto-fixed

Anything outside the table above is **never** rewritten by `--fix-policies`,
including:

- Invalid branch/`latest` includes (`GLCI-INCLUDE-VERSIONS-001` / `002`)
- “Must not use `:latest`” / regex-only image rules without digest remediation
- “Image lag behind registry latest” (needs a tag bump, not only a digest pin)
- Builtin baseline / variable / API policies
- Custom org policies without a registered remediation

If a failed policy is unsupported, the CLI prints a warning and continues.
