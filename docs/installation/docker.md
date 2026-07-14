# Docker

A pre-built Docker image is published by
[MaturityBuilder](https://github.com/MaturityBuilder/gitlab-compliance) for
containerized CI and local smoke tests.

`gitlab-compliance` is published on [Docker
Hub](https://hub.docker.com/r/maturitybuilder/gitlab-compliance/) as
`maturitybuilder/gitlab-compliance`.

## Run a local compliance check

```bash
docker run --rm -it \
  -v "$PWD:/src" \
  -w /src \
  -e GITLAB_TOKEN \
  maturitybuilder/gitlab-compliance \
  gitlab-compliance check -f policies/security/ -p .gitlab-ci.yml --include-nested
```

Add `--project my-group/my-project` when API-backed policies need GitLab project
settings or CI variables.

## Generate pipeline documentation

```bash
docker run --rm -it \
  -v "$PWD:/src" \
  -w /src \
  maturitybuilder/gitlab-compliance \
  gitlab-compliance generate -i .gitlab-ci.yml --format swagger-markdown -o pipeline-reference.md
```

## GitLab CI job

```yaml
gitlab-compliance:
  image: maturitybuilder/gitlab-compliance
  script:
    - gitlab-compliance check -f policies/security/ -p .gitlab-ci.yml --include-nested
```

Depending on your workflow and security policy the pipeline can potentially auto
resolve include refs and pin container image digests by passing `--fix`.

Next: [Usage](../usage/index.md).
