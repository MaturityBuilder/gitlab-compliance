# Docker

A pre-built Python Alpine image is published as
[`maturitybuilder/gitlab-compliance`](https://hub.docker.com/r/maturitybuilder/gitlab-compliance).

Use the container when you do not want to install Python dependencies in the
calling project. Mount the repository that contains `.gitlab-ci.yml` and run the
same CLI command you would use locally.

## Run a local check

```bash
docker run --rm -it \
  -v "$PWD:/work" \
  -w /work \
  maturitybuilder/gitlab-compliance:latest \
  gitlab-compliance check -f policies/security/ -p .gitlab-ci.yml
```

For API-backed policies, pass the GitLab token through the environment and set a
project or group path:

```bash
docker run --rm -it \
  -v "$PWD:/work" \
  -w /work \
  -e GITLAB_TOKEN \
  maturitybuilder/gitlab-compliance:latest \
  gitlab-compliance check -f policies/security/ -p .gitlab-ci.yml \
  --project my-group/my-project --strict
```

## GitLab CI example

```yaml
gitlab-compliance:
  image: maturitybuilder/gitlab-compliance:latest
  stage: test
  script:
    - gitlab-compliance check -f policies/security/ -p .gitlab-ci.yml
```

Depending on your workflow and security policy, the pipeline can optionally
resolve include updates and pin container images by passing `--fix`.

Next: [Usage](../usage/index.md).
