# Docker

A pre-built image is published as
[`maturitybuilder/gitlab-compliance`](https://hub.docker.com/r/maturitybuilder/gitlab-compliance).
Use an immutable digest in production when your supply-chain policy requires it.

## Run locally

Mount your repository into the container and point the CLI at your policies and
pipeline file:

```bash
docker run --rm \
  -v "$PWD:/work" \
  -w /work \
  maturitybuilder/gitlab-compliance:latest \
  gitlab-compliance check -f policies/security/ -p .gitlab-ci.yml
```

For API-backed policies, pass a GitLab token and project or group:

```bash
docker run --rm \
  -v "$PWD:/work" \
  -w /work \
  -e GITLAB_TOKEN \
  maturitybuilder/gitlab-compliance:latest \
  gitlab-compliance check \
    -f policies/security/ \
    -p .gitlab-ci.yml \
    --project my-group/my-project \
    --strict
```

## GitLab CI job

```yaml
compliance:
  image: maturitybuilder/gitlab-compliance:latest
  stage: test
  script:
    - gitlab-compliance check -f policies/security/ -p .gitlab-ci.yml
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

## Auto-fix supported findings

Depending on your workflow and credentials, `--fix` can update supported include
refs and pin container images before checks run:

```bash
gitlab-compliance check -f policies/security/ -p .gitlab-ci.yml --fix
```

Next: [Usage](../usage/index.md).
