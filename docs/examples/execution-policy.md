# Execution Policy

Control **when** pipeline jobs run. Jobs without `rules:` can execute on every push, tag, or schedule — including deploy stages that should be gated to protected branches or merge requests.

## Bad

```yaml
deploy-production:
  stage: deploy
  script:
    - ./deploy.sh
  # no rules — runs on every pipeline source
```

```yaml
release:
  stage: publish
  rules:
    - when: always
```

## Good

```yaml
deploy-production:
  stage: deploy
  script:
    - ./deploy.sh
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
      when: manual
    - when: never

scan:
  stage: test
  script:
    - ./scan.sh
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

## Policy

From [`security/execution-policy.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/examples/example-policies/security/execution-policy.feature):

```gherkin
Feature: Pipeline execution controls

  Scenario: Deploy jobs must define rules
    Given I have any job defined
    When its stage is deploy
    Then it must contain rules

  Scenario: Jobs with rules must include conditional guards
    Given I have any job defined
    When it has rules
    Then its rules must match "if:"

  Scenario: Non-template jobs must define rules
    Given I have any job defined
    When its name does not start with "."
    Then it must contain rules
```

Legacy file [`rules.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/examples/example-policies/security/rules.feature) remains for backward compatibility.

## Consume in GitLab CI (project level)

Pair the execution policy with a compliance job in the same project:

```yaml
stages:
  - test
  - build
  - deploy

include:
  - local: example-ci/compliance-jobs.yml

compliance:
  extends: .compliance:offline

deploy-production:
  stage: deploy
  script:
    - ./deploy.sh
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
      when: manual
    - when: never
```

Warn-only rollout:

```yaml
compliance:
  extends: .compliance:offline
  allow_failure: true
```

Remove `allow_failure` once every job has proper `rules:`.

See also [`example-ci/.gitlab-ci.consumer.yml`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/example-ci/.gitlab-ci.consumer.yml) for a minimal consumer project.

## Org-wide rollout (GitLab Pipeline Execution Policy)

For GitLab tiers with [Pipeline execution policies](https://docs.gitlab.com/user/application_security/policies/pipeline_execution_policies/), inject the compliance job into every member project from a security policy project.

**1. Security policy project** — [`.gitlab/security-policies/policy.yml`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/examples/example-gitlab-execution-policy/.gitlab/security-policies/policy.yml):

```yaml
pipeline_execution_policy:
  - name: Enforce GitLab CI compliance
    description: Injects gitlab-compliance job into member project pipelines
    enabled: true
    pipeline_config_strategy: inject_policy
    content:
      include:
        - project: my-group/gitlab-compliance-policies
          file: policy-ci.yml
          ref: "1.0.0"
    policy_scope:
      projects:
        including:
          - full_path: my-group/*
```

**2. Injected CI config** — [`policy-ci.yml`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/examples/example-gitlab-execution-policy/policy-ci.yml) in the same repo:

```yaml
stages:
  - compliance
  - test
  - build

policy::gitlab-compliance:
  stage: compliance
  image: python:3.12
  script:
    - pip install --quiet gitlab-compliance
    - gitlab-compliance check -f policies/security/ -p .gitlab-ci.yml
        --project "$CI_PROJECT_PATH" --strict
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

The injected job runs the same Gherkin pack (`policies/security/execution-policy.feature`) as project-level consumption. Vendor `examples/example-policies/security/` into `policies/security/` in the security policy repo.

Full walkthrough: [Pipeline Execution Policy](../ci-cd/pipeline-execution-policy.md).

## Run locally

```bash
cp -r examples/example-policies/security/ policies/security/
gitlab-compliance check -f policies/security/ -p .gitlab-ci.yml
```

Back to [Examples](index.md).
