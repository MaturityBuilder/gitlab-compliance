# Template Extends

Jobs should extend organization template jobs (for example shared security or deploy config) instead of duplicating or bypassing them.

## Policy

From [`security/template-extends.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/examples/example-policies/security/template-extends.feature):

```gherkin
Scenario: Code-quality jobs must extend gitleaks template
  Given I have any job defined
  When its stage is code-quality
  Then it must contain extends
  And its extends must include ".gitleaks-template"

Scenario: Deploy jobs must extend approved deploy template
  Given I have any job defined
  When its stage is deploy
  Then its extends must include ".approved-deploy-template"
```

Adjust template names to match your organization's hidden job keys.

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
