# Service Pinning

Service containers (for example `docker:dind`) should use explicit versions.

## Bad

```yaml
build:
  services: [docker:dind]
```

## Good

```yaml
build:
  services: [docker:24.0.5-dind]
```

## Policy

From [`security/service-pinning.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/examples/example-policies/security/service-pinning.feature):

```gherkin
Scenario: docker:dind must include a version
  Given I have any job defined
  When it has services
  Then its services must not match "docker:dind$"
  And its services must match "docker:[0-9]+\\.[0-9]+\\.[0-9]+-dind"
```

## Consume in GitLab CI

Offline policy:

```yaml
include:
  - local: example-ci/compliance-jobs.yml

compliance:
  extends: .compliance:offline
```

## Run locally

```bash
gitlab-compliance check -f policies/security/ -p .gitlab-ci.yml
```

Back to [Examples](index.md).
