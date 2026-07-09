# GitLab CI/CD

Run `gitlab-compliance` in your pipeline so policy violations fail before merge.

## Quick start

Single job gating merge requests and default-branch pipelines:

```yaml
compliance:
  image: python:3.12
  stage: test
  script:
    - pip install gitlab-compliance
    - gitlab-compliance check -f policies/security/ -p .gitlab-ci.yml
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

Copy policies first:

```bash
cp -r examples/example-policies/security/ policies/security/
```

## Include shared compliance jobs

Reuse hidden job templates from
[`example-ci/compliance-jobs.yml`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/example-ci/compliance-jobs.yml):

**Local include** (vendored in your repo):

```yaml
include:
  - local: example-ci/compliance-jobs.yml

compliance:
  extends: .compliance:offline
```

**Central repo include** (versioned distribution):

```yaml
include:
  - project: my-group/gitlab-compliance-policies
    file: example-ci/compliance-jobs.yml
    ref: "1.0.0"

compliance:
  extends: .compliance:offline
```

Minimal consumer example:
[`example-ci/.gitlab-ci.consumer.yml`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/example-ci/.gitlab-ci.consumer.yml).

- **`.compliance:offline`:** YAML-only policies
- **`.compliance:api`:** API-backed policies with `--project` and `--strict`
- **`.compliance:codequality`:** GitLab Code Quality report artifact
- **`.compliance:oci`:** Policies from OCI registry with `--update`

## Policy source options

- **Local directory:** `-f policies/security/` - Default for most projects
- **OCI registry:**
  - `-f oci://registry/...`
  - See [OCI Policy Packs](../examples/oci-policy-packs.md)
- **Git include:** Vendor policies via `include:project` - Central security repo

OCI consumption:

```yaml
compliance:
  extends: .compliance:oci
  variables:
    COMPLIANCE_OCI: oci://registry.example.com/org/gitlab-ci-policies:1.0.0
```

## API-backed policies

`CI_JOB_TOKEN` and `CI_PROJECT_PATH` are set automatically in GitLab CI:

```yaml
compliance:
  extends: .compliance:api
```

Use for [API hardening](../examples/api-hardening.md) and when `--strict` must
fail skipped API scenarios.

**Include release checks** only need a token - `--project` is not required for
comparing pinned include refs against GitLab tags. Token is still required:

```yaml
compliance:includes:
  image: python:3.12
  script:
    - pip install gitlab-compliance
    - gitlab-compliance check -f policies/security/ -p .gitlab-ci.yml
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
```

Use a [project access
token](https://docs.gitlab.com/ee/user/project/settings/project_access_tokens.html)
when `CI_JOB_TOKEN` lacks access to included projects.

## Reports

### Code Quality

Surface findings in the merge request **Changes** tab:

```yaml
compliance:
  extends: .compliance:codequality
```

Artifact: `gl-code-quality-report.json` (configured in the template).

### MR comment

```yaml
comment-compliance:
  image: python:3.12
  script:
    - pip install gitlab-compliance
    - >-
      gitlab-compliance check
      -f policies/security/
      -p .gitlab-ci.yml
      --format mr-comment
      -o comment.md
      || true
    - |
      curl --request POST \
        --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
        --data-urlencode "body@$(cat comment.md)" \
        "$CI_API_V4_URL/projects/$CI_PROJECT_ID/merge_requests/$CI_MERGE_REQUEST_IID/notes"
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
```

Store `GITLAB_TOKEN` as a masked CI variable with `api` scope.

## Rollout

Start warn-only, then enforce:

```yaml
compliance:
  extends: .compliance:offline
  allow_failure: true   # remove once baseline is clean
```

Pair with [Execution Policy](../examples/execution-policy.md) policies to catch
jobs missing `rules:` before blocking.

## Org-wide enforcement

For GitLab tiers with security policies, inject the compliance job into every
member project via a **Pipeline Execution Policy** instead of adding a job to
each `.gitlab-ci.yml`.

See [Pipeline Execution Policy](pipeline-execution-policy.md) for the full
walkthrough using
[`examples/example-gitlab-execution-policy/`](https://github.com/MaturityBuilder/gitlab-compliance/tree/main/examples/example-gitlab-execution-policy).

Back to [Using in CI/CD](index.md).
