# GitLab Compliance Security Examples

This guide shows how to use `gitlab-compliance` (PyPI package `gitlab-docs`) the same way [terraform-compliance](https://github.com/terraform-compliance/cli) enforces infrastructure policies — but for GitLab CI YAML and project settings.

## Policy documentation annotations

Compliance policies support [Conftest-style metadata](https://www.conftest.dev/documentation/) blocks so policies can be indexed with IDs, titles, and descriptions.

```gherkin
# METADATA
# title: Container images must be pinned
# description: Job images must use explicit versions or digests.
# custom:
#   id: GLCI-IMAGE-PINNING
#   severity: HIGH
Feature: Container images must be pinned

# METADATA
# title: Disallow latest image tags
# description: Prevents jobs from using mutable latest tags.
# custom:
#   id: GLCI-IMAGE-PINNING-001
  Scenario: Job images must not use the latest tag
    Given I have any job defined
    When it has image
    Then its image must not match ":latest$"
```

Generate a searchable catalog:

```bash
gitlab-compliance compliance-doc -f policies/ -o COMPLIANCE-POLICIES.md
gitlab-compliance compliance-doc -f policies/ --format html -o COMPLIANCE-POLICIES.html
```

If `custom.id` is omitted, IDs are generated automatically (for example `GLCI-IMAGE-PINNING-001`). Compliance reports include policy IDs and titles in console, markdown, HTML, and MR comment output.

## Sharing policies via OCI registries

Like [Conftest](https://www.conftest.dev/sharing/), policy packs can be stored in OCI-compliant registries (GitLab Container Registry, GHCR, ACR, ECR, etc.).

```bash
# Authenticate first
docker login registry.example.com

# Publish a policy pack
gitlab-compliance compliance-push -f policies/ registry.example.com/org/gitlab-ci-policies:1.0.0

# Pull policies locally (default directory: policy/)
gitlab-compliance compliance-pull oci://registry.example.com/org/gitlab-ci-policies:1.0.0 -o policies/

# Run compliance directly from the registry
gitlab-compliance compliance -f oci://registry.example.com/org/gitlab-ci-policies:1.0.0 -p .gitlab-ci.yml

# Force a fresh pull before running
gitlab-compliance compliance -f oci://registry.example.com/org/gitlab-ci-policies:1.0.0 -p .gitlab-ci.yml --update
```

Policy bundles are published as `application/vnd.gitlab-docs.policy.bundle.v1+tar+gzip` OCI artifacts containing your `.feature` files.

## Quick start

```bash
# Copy the example security policy pack
cp -r example-policies/security/ policies/

# Run against your pipeline (offline, YAML only)
gitlab-compliance compliance -f policies/ -p .gitlab-ci.yml

# Gate merge requests with API-backed checks
gitlab-compliance compliance -f policies/ -p .gitlab-ci.yml --project $CI_PROJECT_PATH
```

## Security risks and policies

| Risk | Bad config | Policy file |
|------|------------|-------------|
| Floating images | `image: docker:latest` | `security/image-pinning.feature` |
| Unpinned components | `component: ...@main` | `security/component-pinning.feature` |
| Unpinned fragments | `ref: main` on project includes | `security/fragment-pinning.feature` |
| Unpinned services | `services: [docker:dind]` | `security/service-pinning.feature` |
| Missing rules | Jobs without `rules:` | `security/rules.feature` |
| Bypassing templates | Jobs not extending org templates | `security/template-extends.feature` |
| Public job logs | `public_jobs: true` (API) | `security/api-hardening.feature` |
| Exposed CI variables | Unmasked secrets (API) | `security/api-hardening.feature` |

## Pin job images

**Bad:**

```yaml
scan:
  image: python
build:
  image: docker:latest
```

**Policy** (`security/image-pinning.feature`):

```gherkin
Scenario: Job images must not use the latest tag
  Given I have any job defined
  When it has image
  Then its image must not match ":latest$"
```

## Pin CI/CD components

**Bad:**

```yaml
include:
  - component: gitlab.com/org/pipeline@main
```

**Good:**

```yaml
include:
  - component: gitlab.com/org/pipeline@1.2.0
```

**Policy** (`security/component-pinning.feature`):

```gherkin
Scenario: Component includes must use semver
  Given I have include type "component" defined
  Then its version must match "^\d+\.\d+\.\d+(-[\w.]+)?$"
```

## Pin shared fragments

**Bad:**

```yaml
include:
  - project: platform/ci-templates
    ref: main
    file: security/gitleaks.yml
```

**Good:**

```yaml
include:
  - project: platform/ci-templates
    ref: 2.4.1
    file: security/gitleaks.yml
```

## Pin service images

**Bad:**

```yaml
build:
  services: [docker:dind]
```

**Good:**

```yaml
build:
  services: [docker:24.0.5-dind]
```

## API-backed hardening

Requires `--project`, a GitLab token, and optionally `--group` for group-scoped checks.

API-backed scenarios are **skipped by default** when connection info is missing (no token and/or no `--project`/`--group`). Use `--strict` to fail those scenarios instead — useful in CI jobs that must enforce API checks.

```bash
# Offline YAML checks only; API scenarios skipped
gitlab-compliance compliance -f policies/ -p .gitlab-ci.yml

# Fail if API connection info is missing
gitlab-compliance compliance -f policies/ -p .gitlab-ci.yml --strict

# Full checks with API
gitlab-compliance compliance -f policies/ -p .gitlab-ci.yml --project $CI_PROJECT_PATH
```

```gherkin
Scenario: Job logs must not be public
  Given I have project setting "public_jobs" defined
  Then its value must be false
```

## Rollout strategy

1. **Warn-only** — run in a CI job with `allow_failure: true`
2. **Block** — remove `allow_failure` once baselines are fixed
3. **Central policies** — version `policies/` in a security repo; teams sync or include via `include:project`

## Consumer CI job

```yaml
compliance:
  image: python:3.12
  script:
    - pip install gitlab-docs
    - gitlab-compliance compliance -f policies/ -p .gitlab-ci.yml --project $CI_PROJECT_PATH
    - gitlab-compliance compliance -f policies/ -p .gitlab-ci.yml --format mr-comment -o compliance-mr-comment.md
  artifacts:
    reports:
      dotenv: compliance-mr-comment.md
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
```

## Output formats

| Format | Use case | Example |
|--------|----------|---------|
| `console` | Local dev / CI logs (default, Rich tables) | `gitlab-compliance compliance -f policies/ -p .gitlab-ci.yml` |
| `markdown` | Docs, wikis, artifacts | `--format markdown -o COMPLIANCE-REPORT.md` |
| `html` | Human-readable report | `--format html -o COMPLIANCE-REPORT.html` |
| `mr-comment` | Post as GitLab MR note | `--format mr-comment -o compliance-mr-comment.md` |
| `codequality` | GitLab Code Quality MR/pipeline report | `--format codequality -o gl-code-quality-report.json` |

Publish Code Quality findings in CI:

```yaml
compliance:
  script:
    - pip install gitlab-docs
    - gitlab-compliance compliance -f policies/ -p .gitlab-ci.yml --format codequality -o gl-code-quality-report.json
  artifacts:
    reports:
      codequality: gl-code-quality-report.json
```

Post MR comment in CI:

```yaml
comment-compliance:
  script:
    - pip install gitlab-docs
    - gitlab-compliance compliance -f policies/ -p .gitlab-ci.yml --format mr-comment -o comment.md || true
    - |
      curl --request POST \
        --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
        --data-urlencode "body@$(cat comment.md)" \
        "$CI_API_V4_URL/projects/$CI_PROJECT_ID/merge_requests/$CI_MERGE_REQUEST_IID/notes"
```
