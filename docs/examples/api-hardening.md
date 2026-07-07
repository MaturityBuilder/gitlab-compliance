# API Hardening

Some controls cannot be expressed in YAML alone. API-backed scenarios read project settings and CI variables via the GitLab API.

Requires `--project`, a token, and optionally `--strict` in CI. See [Environment Variables](../usage/environment-variables.md).

## Policy examples

From [`security/api-hardening.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/examples/example-policies/security/api-hardening.feature):

```gherkin
Scenario: Job logs must not be public
  Given I have project setting "public_jobs" defined
  Then its value must be false

Scenario: Auto DevOps must be disabled
  Given I have project setting "auto_devops_enabled" defined
  Then its value must be false

Scenario: Production tokens must be protected and masked
  Given I have any project ci variable defined
  When its key matches "^(AWS_|DATABASE_|API_KEY)"
  Then its protected must be true
  And its masked must be true
```

## Consume in GitLab CI

API-backed policy — requires `--project` and `--strict`:

```yaml
include:
  - local: example-ci/compliance-jobs.yml

compliance:
  extends: .compliance:api
```

`CI_JOB_TOKEN` and `CI_PROJECT_PATH` are set automatically in GitLab CI jobs.

With Code Quality reporting:

```yaml
compliance:api:
  extends: .compliance:api

compliance:report:
  extends: .compliance:codequality
  needs: [compliance:api]
```

## Run locally

```bash
export GITLAB_TOKEN="<token>"
gitlab-compliance compliance -f policies/security/ -p .gitlab-ci.yml \
  --project my-group/my-project --strict
```

Without API credentials, these scenarios are **skipped** unless `--strict` is set.

Back to [Examples](index.md).
