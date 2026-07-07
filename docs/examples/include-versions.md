# Include Versions

Validate `include:` refs use immutable semver tags and optionally check whether a newer release exists on the included project.

## Offline: valid semver

Project and component includes should pin semver refs instead of branch names.

**Bad:**

```yaml
include:
  - project: platform/ci-templates
    ref: main
    file: security/gitleaks.yml
  - component: gitlab.com/org/pipeline@develop
```

**Good:**

```yaml
include:
  - project: platform/ci-templates
    ref: 2.4.1
    file: security/gitleaks.yml
  - component: gitlab.com/org/pipeline@1.2.0
```

**Policy** (offline):

```gherkin
Scenario: Project includes must use valid semver
  Given I have include type "project" defined
  Then it must use valid semver
```

## API-backed: latest release available (Advanced)

When a GitLab token is available, `gitlab-compliance` resolves the included project or component path and compares the pinned semver tag against the highest semver tag returned by the GitLab API.

Requires `GITLAB_TOKEN` or `CI_JOB_TOKEN`. A token alone is enough — `--project` is not required for include release lookups. Scenarios skip when no token is set unless `--strict` is used.

**Policy:**

```gherkin
Scenario: Includes must not lag behind the latest release
  Given I have any include with release metadata defined
  Then a newer release must not be available
```

Filter to only outdated includes:

```gherkin
Scenario: Outdated includes must be upgraded
  Given I have any include with release metadata defined
  When a newer release is available
  Then it must track the latest release
```

## Supply chain age policies

For supply chain security, strict “must be latest” checks can be too aggressive. Use **days-based thresholds** when a GitLab token resolves tag commit dates from the API.

### Grace period (adoption window)

Allow `{days}` after a new release ships before requiring an upgrade. Fails when a newer semver exists **and** the latest tag was committed more than `{days}` days ago.

```gherkin
Scenario: New releases get a 30-day adoption window
  Given I have any include with release metadata defined
  Then a newer release must not be available for more than 30 days
```

### Maximum release lag

Fail when a newer semver exists **and** the pinned tag is more than `{days}` days older than the latest tag (by commit dates).

```gherkin
Scenario: Includes must stay within 90 days of upstream
  Given I have any include with release metadata defined
  Then its release lag must not exceed 90 days
```

Filter severely lagging includes before asserting upgrade:

```gherkin
Scenario: Flag severely lagging includes
  Given I have any include with release metadata defined
  When its release lag exceeds 90 days
  Then it must track the latest release
```

### Within the latest N semver tags

Require the pinned ref to rank among the **N highest semver tags** on the included project (rank 1 = latest). More flexible than strict latest-only — allows staying one or two releases behind.

```gherkin
Scenario: Includes must be within the latest three semver tags
  Given I have any include with release metadata defined
  Then it must be within the latest 3 tags
```

Filter includes outside the window:

```gherkin
Scenario: Flag includes outside the latest five tags
  Given I have any include with release metadata defined
  When it is not within the latest 5 tags
  Then it must track the latest release
```

## Entity fields

| Field | Description |
|-------|-------------|
| `version` | Pinned `ref` or component version |
| `valid_version` | `true` when `version` is valid semver |
| `latest_version` | Highest semver tag from GitLab API |
| `update_available` | `true` when `latest_version` is newer than `version` |
| `version_released_at` | ISO timestamp of the pinned tag commit |
| `latest_version_released_at` | ISO timestamp of the latest semver tag commit |
| `latest_release_age_days` | Days since the latest tag was committed |
| `release_lag_days` | Days between pinned and latest tag commits (when outdated) |
| `version_tag_rank` | 1-based rank among semver tags (1 = latest) |
| `semver_tag_count` | Total semver tags on the included project |

## Include types

| Type | Parsed | Version field | API enrichment |
|------|--------|---------------|----------------|
| `project` | Yes | `ref:` | GitLab project tags |
| `component` | Yes | `@version` | GitLab component project tags |
| `template` | Yes | `n/a` (instance-bundled) | Skipped — prefer `remote:` with version in URL |
| `remote` | Yes | semver/SHA from URL path | URL pin check only |
| `local` | Yes | `n/a` | Skipped |

## Auto-fix (`--fix`)

Bump outdated project/component includes to the latest semver tag detected via GitLab API:

```bash
export GITLAB_TOKEN="<token>"
gitlab-compliance compliance -f policies/security/ -p .gitlab-ci.yml --fix
```

## Consume in GitLab CI

Semver validation (offline):

```yaml
include:
  - local: example-ci/compliance-jobs.yml

compliance:
  extends: .compliance:offline
```

Release availability checks (API — `CI_JOB_TOKEN` is set automatically in GitLab CI):

```yaml
compliance:
  extends: .compliance:api
```

The `.compliance:api` template passes `--project $CI_PROJECT_PATH --strict` for project settings; include release metadata is enriched whenever a token is present.

## Run locally

```bash
export GITLAB_TOKEN="<token>"
gitlab-compliance compliance -f policies/security/ -p .gitlab-ci.yml
```

Full example pack: [`security/include-versions.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/examples/examples/example-policies/security/include-versions.feature).

Back to [Examples](index.md).
