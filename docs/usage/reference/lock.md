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
# Create or refresh the lock
gitlab-compliance lock generate -p .gitlab-ci.yml -l .gitlab-ci.lock
gitlab-compliance lock update -p .gitlab-ci.yml

# Fail CI when inventory drifts from the committed lock
gitlab-compliance lock verify -p .gitlab-ci.yml

# Print fingerprint (optionally as a GitLab dotenv report)
gitlab-compliance lock fingerprint -p .gitlab-ci.yml
gitlab-compliance lock fingerprint --from-lock --dotenv lock.env
```

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

## Offline by default

`lock generate` works without a GitLab token. Pass `--enrich` (with a token) to
resolve include release metadata and container digests into the inventory when
you want registry-backed pins recorded.

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
  update       Refresh `.gitlab-ci.lock` (alias for generate).
  verify       Fail when the current inventory fingerprint differs from...
```
