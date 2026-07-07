# GIVEN Directives

`Given` sets the initial **stash** — the list of entities the scenario will filter and assert on. Every scenario needs at least one `Given`.

You cannot use `And` with a `Given` that changes entity type; use another `Given` step or a separate scenario.

## Reference

### `Given I have any job defined`

All jobs from the pipeline YAML (including from resolved local includes).

```gherkin
Given I have any job defined
```

### `Given I have job "{name}" defined`

A single job by name (case-sensitive).

```gherkin
Given I have job "build" defined
```

### `Given I have any include defined`

All `include:` entries (local, remote, component, template).

```gherkin
Given I have any include defined
```

### `Given I have include type "{include_type}" defined`

Includes filtered by type: `local`, `file`, `remote`, `template`, `component`, `artifact`, etc.

```gherkin
Given I have include type "component" defined
```

### `Given I have any variable defined`

Pipeline-level `variables:` entries.

```gherkin
Given I have any variable defined
```

### `Given I have any workflow rule defined`

Entries under `workflow: rules:`.

```gherkin
Given I have any workflow rule defined
```

### `Given I have any project setting defined`

**API:** all project settings fetched for `--project`. Skipped without API connection unless `--strict`.

```gherkin
Given I have any project setting defined
```

### `Given I have project setting "{name}" defined`

**API:** a single project setting by key (for example `public_jobs`, `auto_devops_enabled`).

```gherkin
Given I have project setting "public_jobs" defined
```

### `Given I have any project ci variable defined`

**API:** CI/CD variables for the project.

```gherkin
Given I have any project ci variable defined
```

### `Given I have any group setting defined`

**API:** group-level settings when `--group` is set.

```gherkin
Given I have any group setting defined
```

### `Given I have any include with release metadata defined`

**API:** includes where release metadata was resolved from GitLab (requires token).

Enriched include entities expose:

| Field | Description |
|-------|-------------|
| `version_released_at` | ISO timestamp of the pinned tag commit |
| `latest_version_released_at` | ISO timestamp of the latest semver tag commit |
| `latest_release_age_days` | Days since the latest tag was committed |
| `release_lag_days` | Days between pinned and latest tag commits (when outdated) |
| `version_tag_rank` | 1-based rank among semver tags (1 = latest) |
| `semver_tag_count` | Total semver tags on the included project |

```gherkin
Given I have any include with release metadata defined
```

### Container image entities

| Field | Description |
|-------|-------------|
| `image` | Full image reference from job `image:` or `services:` |
| `latest_version` | Highest semver tag from the registry |
| `latest_digest` | sha256 digest for the pinned or latest tag |
| `version_tag_rank` | 1-based rank among semver tags (1 = latest) |

```gherkin
Given I have any container image defined
Given I have container image from "job" defined
Given I have any container image with release metadata defined
```

Next: [WHEN Directives](when.md).
