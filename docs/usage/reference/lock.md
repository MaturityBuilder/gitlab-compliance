# lock

Build and verify a `.gitlab-ci.lock` inventory of pipeline dependencies.

    The lockfile records includes, images, services, external steps, and
    pipeline structure so CI can skip gitlab-compliance jobs when nothing
    inventory-relevant has changed (fingerprint or ``rules:changes``).

<!-- MANUAL DOCS:START -->

## What it is

`.gitlab-ci.lock` is a committed **inventory** of your pipeline closure — similar
in spirit to a package lockfile, but for GitLab CI configuration:

- Includes (local, remote, project, component, template)
- Job images and service images
- External steps (components, templates, `trigger:` jobs)
- Pipeline structure (jobs, stages, variables, workflow rules)
- Optional policy-pack hash (`-f` / `--features`)

It is **not** only a supply-chain pinning tool. Use it as the single artifact
that answers: "has anything gitlab-compliance cares about changed?"

## Commands

```bash
# Create or refresh the lock (Rich inventory report by default)
gitlab-compliance lock generate -p .gitlab-ci.yml -l .gitlab-ci.lock
gitlab-compliance lock update -p .gitlab-ci.yml

# Fail CI when inventory drifts from the committed lock
gitlab-compliance lock verify -p .gitlab-ci.yml

# Print fingerprint (optionally as a GitLab dotenv report)
gitlab-compliance lock fingerprint -p .gitlab-ci.yml
gitlab-compliance lock fingerprint --from-lock --dotenv lock.env
```

### Modern terminal UX

Interactive runs show a Plumber-style report:

- Progress spinner while scanning
- Health / coverage banner (resolved includes + digest-pinned images)
- Metric cards for jobs, includes, images, external steps
- Inventory tables and external-step tree
- Drift panel + next-step guidance on verify failures

Scripting flags:

| Flag | Purpose |
| ---- | ------- |
| `--quiet` / `-q` | Fingerprint-only output |
| `--json` | Machine-readable report |
| `--verbose` / `-v` | Full tables (no truncation) |

Include your policy directory in the inventory hash so policy edits also bump
the fingerprint:

```bash
gitlab-compliance lock generate -p .gitlab-ci.yml -f policies/
```

## Skip compliance jobs when nothing changed

Commit `.gitlab-ci.lock` and gate heavy jobs with GitLab `rules:changes`:

```yaml
compliance:
  stage: test
  script:
    - pip install gitlab-compliance
    - gitlab-compliance lock verify -p .gitlab-ci.yml -f policies/
    - gitlab-compliance check -f policies/ -p .gitlab-ci.yml
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
      changes:
        - .gitlab-ci.yml
        - .gitlab-ci.lock
        - "**/*gitlab-ci*.yml"
        - policies/**/*
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

Or export the fingerprint as a dotenv artifact for cache keys / child pipelines:

```yaml
inventory:
  script:
    - gitlab-compliance lock fingerprint -p .gitlab-ci.yml --dotenv lock.env
  artifacts:
    reports:
      dotenv: lock.env
```

The dotenv key is `GITLAB_COMPLIANCE_LOCK_FINGERPRINT`.

## Upstream includes and image digests

By default `lock generate` / `update` / `verify`:

- Walks the **full upstream include closure** (`remote:`, `project:`, and
  GitLab `template:` includes when reachable)
- Records a **content hash** for each fetched include YAML
- Attempts **image digests** for job/service images (Docker Hub without a
  token; GitLab Container Registry when `--token` / `GITLAB_TOKEN` is set)
- Resolves include **release metadata** when a GitLab token is available

Only **declared** digests (image refs already pinned with `@sha256:…` in YAML)
and include content hashes affect the fingerprint. Registry-resolved digests
are stored as advisory `resolvedDigest` fields for the report UX and do not
change the fingerprint across online/offline environments.

CI components are still inventory-declared (identity/ref) but cannot be merged
from the GitLab API the same way.

### Untrusted pipelines

Default lock commands fetch whatever `include:remote` / nested remotes the
YAML names. For merge requests from untrusted sources, prefer offline mode:

```bash
gitlab-compliance lock generate -p .gitlab-ci.yml \
  --no-resolve-external-includes \
  --no-enrich
```

For a fully offline inventory (no network) on trusted pipelines, use the same
flags.

<!-- MANUAL DOCS:END -->

## Usage

```
Usage: gitlab-compliance lock [OPTIONS] COMMAND [ARGS]...
```

## Options
* `help`:
  * Type: BOOL
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.


## CLI Help

```
Usage: gitlab-compliance lock [OPTIONS] COMMAND [ARGS]...

  Build and verify a `.gitlab-ci.lock` inventory of pipeline dependencies.

  The lockfile records includes, images, services, external steps, and
  pipeline structure so CI can skip gitlab-compliance jobs when nothing
  inventory-relevant has changed (fingerprint or ``rules:changes``).

Options:
  --help  Show this message and exit.

Commands:
  fingerprint  Print the inventory fingerprint (for CI skip / cache keys).
  generate     Create or overwrite `.gitlab-ci.lock` from the current...
  update       Refresh `.gitlab-ci.lock` with a modern inventory report.
  verify       Fail when the current inventory fingerprint differs from...
```
