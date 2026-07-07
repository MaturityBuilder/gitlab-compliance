# Fragment Pinning

Shared YAML from other projects must pin `ref:` to a tag or SHA, not a moving branch.

## Bad

```yaml
include:
  - project: platform/ci-templates
    ref: main
    file: security/gitleaks.yml
```

## Good

```yaml
include:
  - project: platform/ci-templates
    ref: 2.4.1
    file: security/gitleaks.yml
```

## Policy

From [`security/fragment-pinning.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/examples/example-policies/security/fragment-pinning.feature):

```gherkin
Scenario: Project includes must not use branch refs
  Given I have include type "project" defined
  Then its version must not match "^(main|master|develop)$"

Scenario: Project includes must use valid semver
  Given I have include type "project" defined
  Then its version must match "^\\d+\\.\\d+\\.\\d+"
```

## Consume in GitLab CI

Offline policy:

```yaml
include:
  - local: example-ci/compliance-jobs.yml

compliance:
  extends: .compliance:offline
```

Pair with [Include Versions](include-versions.md) when you also want API-backed release checks.

## Run locally

```bash
gitlab-compliance compliance -f policies/security/ -p .gitlab-ci.yml
```

Back to [Examples](index.md).
