# Auto-fix policies (`--fix-policies`)

`--fix-policies` remediates **failed** BDD scenarios only when they match an
explicit allowlist. Unsupported failures are left unchanged and reported as not
auto-fixable.

For each allowlisted failure, only **entities that fail that policy's
predicates** are rewritten (for example, unpinned job images for
`GLCI-BUILTIN-IMAGE-PINNING-001`, or includes outside the adoption window for
`GLCI-BUILTIN-INCLUDE-VERSIONS-004`). Other includes/images in the same pipeline are
left alone.

This is separate from
[`--fix`](reference/check.md#fix) (alias: `--fix-supply-chain`), which rewrites
includes/images before policies run.

## Usage

```bash
gitlab-compliance check -f policies/security/ -p .gitlab-ci.yml \
  --fix-policies --token "$GITLAB_TOKEN"
```

With an MR (`CI_JOB_TOKEN` is rejected for `--create-mr`; use a project or
personal access token):

```bash
gitlab-compliance check -f policies/security/ -p .gitlab-ci.yml \
  --fix-policies --create-mr --project "$CI_PROJECT_PATH" \
  --token "$GITLAB_TOKEN"
```

![gitlab-compliance check create-mr](../demos/gifs/check-create-mr.gif)

Both fix modes can be combined:

```bash
gitlab-compliance check -f policies/security/ -p .gitlab-ci.yml \
  --fix --fix-policies --create-mr --project "$CI_PROJECT_PATH" \
  --token "$GITLAB_TOKEN"
```

Requires a GitLab token. Cannot be combined with `--dry-run`.

## Trust model

Allowlisted remediations use the same GitLab/registry “latest” metadata as
`--fix`. Always review generated YAML (and any `--create-mr`
diff) before merging — a compromised upstream tag or registry can steer pins
and version bumps.

Scenario details, fix messages, and MR comment bodies are scrubbed for common
token patterns and secret environment values before logging or posting.

## Flow

1. Optional `--fix` rewrites.
2. Initial policy run.
3. Allowlisted failed scenarios → YAML remediations for failing entities only.
4. Policies re-run; the final report reflects post-fix status.
5. Optional `--create-mr` commits those edits (report is printed first; MR
   failures exit `2` when compliance otherwise passed).

## Supported remediations

| Policy ID | What it fixes |
| --- | --- |
| `GLCI-BUILTIN-INCLUDE-VERSIONS-003` | Bump include `ref:` / `@version` to latest semver |
| `GLCI-BUILTIN-INCLUDE-VERSIONS-004` | Same (only includes past the 30-day adoption window) |
| `GLCI-BUILTIN-INCLUDE-VERSIONS-005` | Same (only includes with lag over 90 days) |
| `GLCI-BUILTIN-INCLUDE-VERSIONS-006` | Same (only includes outside the latest-N tags window) |
| `GLCI-BUILTIN-IMAGE-PINNING-001` | Pin **job** images to `@sha256:<digest>` |

These IDs match the example policies under
`examples/example-policies/security/`.

## Not auto-fixed

Anything outside the table above is **never** rewritten by `--fix-policies`,
including:

- Invalid branch/`latest` includes (`GLCI-BUILTIN-INCLUDE-VERSIONS-001` / `002`)
- “Must not use `:latest`” / regex-only image rules without digest remediation
- “Image lag behind registry latest” (needs a tag bump, not only a digest pin)
- Service images (unless covered by a future allowlisted policy)
- Builtin baseline / variable / API policies
- Custom org policies without a registered remediation

If a failed policy is unsupported, the CLI prints a warning and continues.
