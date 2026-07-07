# Component Pinning

CI/CD components in `include:` must use immutable version refs, not branch names like `@main`.

## Bad

```yaml
include:
  - component: gitlab.com/org/pipeline@main
```

## Good

```yaml
include:
  - component: gitlab.com/org/pipeline@1.2.0
```

## Policy

From [`security/component-pinning.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/examples/examples/example-policies/security/component-pinning.feature):

```gherkin
Scenario: Component includes must use semver
  Given I have include type "component" defined
  Then its version must match "^\d+\.\d+\.\d+(-[\w.]+)?$"
```

## Consume in GitLab CI

Offline policy — no API token required:

```yaml
include:
  - local: example-ci/compliance-jobs.yml

compliance:
  extends: .compliance:offline
```

The job runs all policies under `policies/security/`, including `component-pinning.feature`.

## Run locally

```bash
gitlab-compliance compliance -f policies/security/ -p .gitlab-ci.yml
```

Scenarios skip when the pipeline has no `component:` includes (not applicable).

Back to [Examples](index.md).
