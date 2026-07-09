# Docker

Run `gitlab-compliance` from the published container image when you do not want
to install Python dependencies on the host.

Image:
[`maturitybuilder/gitlab-compliance`](https://hub.docker.com/r/maturitybuilder/gitlab-compliance)
on Docker Hub.

## Local run

Mount the repository and run `check` from the working tree:

```bash
docker run --rm -it \
  -v "$PWD:/src" \
  -w /src \
  -e GITLAB_TOKEN="$GITLAB_TOKEN" \
  maturitybuilder/gitlab-compliance:latest \
  gitlab-compliance check -f policies/security/ -p .gitlab-ci.yml
```

Add API-backed project checks when a token is available:

```bash
docker run --rm -it \
  -v "$PWD:/src" \
  -w /src \
  -e GITLAB_TOKEN="$GITLAB_TOKEN" \
  maturitybuilder/gitlab-compliance:latest \
  gitlab-compliance check -f policies/security/ -p .gitlab-ci.yml \
    --project my-group/my-project --strict
```

## GitLab CI/CD

```yaml
gitlab-compliance:
  image: maturitybuilder/gitlab-compliance:latest
  stage: test
  script:
    - gitlab-compliance check -f policies/security/ -p .gitlab-ci.yml
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

Depending on your workflow and security policy, the pipeline can auto-resolve
outdated include refs and pin container images by adding `--fix`.

Next: [Usage](../usage/index.md).
