# Pipeline Execution Policy

Inject `gitlab-compliance` into member project pipelines org-wide using GitLab
[Pipeline execution
policies](https://docs.gitlab.com/user/application_security/policies/pipeline_execution_policies/).

## Prerequisites

- GitLab tier with security policies (Ultimate or equivalent feature
  availability)
- A **security policy project** linked to your group or instance
- Policy pack vendored in the security policy repo at `policies/security/` (copy
  from
  [`examples/example-policies/security/`](https://github.com/MaturityBuilder/gitlab-compliance/tree/main/examples/example-policies/security))

## Repository layout

```text
my-group/gitlab-compliance-policies/     # security policy project
├── .gitlab/security-policies/
│   └── policy.yml                       # Pipeline Execution Policy definition
├── policy-ci.yml # CI config injected into member pipelines
└── policies/security/                   # Gherkin .feature files
    ├── execution-policy.feature
    ├── image-pinning.feature
    └── ...
```text

Example artifacts in this repository:
[`examples/example-gitlab-execution-policy/`](https://github.com/MaturityBuilder/gitlab-compliance/tree/main/examples/example-gitlab-execution-policy).

## Step 1: Define the policy

[`.gitlab/security-policies/policy.yml`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/examples/example-gitlab-execution-policy/.gitlab/security-policies/policy.yml):

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
```text

### `inject_policy` vs `inject_ci`

Use **`inject_policy`** (recommended). The deprecated `inject_ci` strategy is
removed in GitLab 19.0 and does not support custom policy stages.

- **`inject_policy`:** Injects policy stages and jobs into member pipelines
- **`inject_ci` (deprecated):** Legacy injection without custom stages
- **`override_project_ci`:** Replaces the project pipeline entirely

## Step 2: Define the injected job

[`policy-ci.yml`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/examples/example-gitlab-execution-policy/policy-ci.yml):

```yaml
stages:
  - compliance
  - test
  - build

policy::gitlab-compliance:
  stage: compliance
  image: python:3.12
  variables:
    COMPLIANCE_POLICIES: policies/security
  script:
    - pip install --quiet gitlab-compliance
    - gitlab-compliance check -f "$COMPLIANCE_POLICIES" -p .gitlab-ci.yml
        --project "$CI_PROJECT_PATH" --strict
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```text

This runs the same Gherkin policies as a [project-level compliance
job](gitlab-ci.md), including [Execution
Policy](../examples/execution-policy.md) scenarios.

## Step 3: Scope the policy

Limit which projects receive the injected job:

```yaml
policy_scope:
  projects:
    including:
      - full_path: my-group/production/*
    excluding:
      - id: 12345
```text

Or scope by compliance framework label:

```yaml
policy_scope:
  compliance_frameworks:
    including:
      - SOX
```text

## Variables and API checks

Pipeline execution policy pipelines run in **isolation** from the member
project's `.gitlab-ci.yml`. Implications:

- `CI_PROJECT_PATH` and `CI_JOB_TOKEN` refer to the **member project** — API
  checks work as expected.
- Custom variables defined only in a member project's `.gitlab-ci.yml` are
  **not** available to the policy job. Define overrides as **project or group
  CI/CD variables** instead.
- For include release checks, ensure the token can read tags on included
  projects.

## Pair with BDD execution policy

The injected job enforces
[`execution-policy.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/examples/example-policies/security/execution-policy.feature)
against each member project's `.gitlab-ci.yml` — catching deploy jobs without
`rules:` and weak `when: always` guards.

See [Execution Policy](../examples/execution-policy.md) for the policy
definition and project-level alternative.

## Related

- [GitLab CI/CD consumption](gitlab-ci.md) — project-level jobs and shared
  templates
- [Examples index](../examples/index.md) — all policy types and consumption
  patterns

Back to [Using in CI/CD](index.md).
