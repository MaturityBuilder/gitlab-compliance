# Installing via Docker

Use the published
[`maturitybuilder/gitlab-compliance`](https://hub.docker.com/r/maturitybuilder/gitlab-compliance/)
image when you want a container-only setup without installing Python packages in
the job.

## Run locally

Mount your repository into the container and run the same commands shown in the
CLI reference:

```bash
docker run --rm -t \
  -v "$PWD:/workspace" \
  -w /workspace \
  maturitybuilder/gitlab-compliance \
  gitlab-compliance check -f policies/security/ -p .gitlab-ci.yml
```

For API-backed checks, pass a token and project or group path:

```bash
docker run --rm -t \
  -v "$PWD:/workspace" \
  -w /workspace \
  -e GITLAB_TOKEN \
  maturitybuilder/gitlab-compliance \
  gitlab-compliance check \
    -f policies/security/ \
    -p .gitlab-ci.yml \
    --project my-group/my-project \
    --strict
```

## Generate documentation

The container can also write generated documentation back to the mounted
workspace:

```bash
docker run --rm -t \
  -v "$PWD:/workspace" \
  -w /workspace \
  maturitybuilder/gitlab-compliance \
  gitlab-compliance generate \
    -i .gitlab-ci.yml \
    --format swagger-markdown \
    -o pipeline-reference.md
```

## GitLab CI example

```yaml
compliance:
  image: maturitybuilder/gitlab-compliance
  stage: test
  script:
    - gitlab-compliance check -f policies/security/ -p .gitlab-ci.yml
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

## Optional auto-fix mode

Depending on your workflow and security policy, `check --fix` can update
outdated GitLab include refs and pin container images to `sha256` digests before
running policies. It requires GitLab and registry access through the job
environment.

```bash
gitlab-compliance check -f policies/security/ -p .gitlab-ci.yml --fix
```

Next: [Usage](../usage/index.md).
