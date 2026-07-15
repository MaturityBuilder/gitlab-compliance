# Docker

![gitlab-compliance](../assets/favicon.svg){ width="120" }

A pre-built Docker image on Python Alpine Linux, published by
[MaturityBuilder](https://github.com/MaturityBuilder/gitlab-compliance).

`gitlab-compliance` is published on [Docker
Hub](https://hub.docker.com/r/maturitybuilder/gitlab-compliance/) as
`maturitybuilder/gitlab-compliance`.

```bash
docker run --rm \
  -v "$PWD:/src" \
  -w /src \
  -e GITLAB_TOKEN \
  maturitybuilder/gitlab-compliance:latest \
  gitlab-compliance check -f example-policies -p .gitlab-ci.yml --include-nested \
  --project my-group/my-project
```

## Audit pipeline YAML

```yml
gitlab-compliance:
  image: maturitybuilder/gitlab-compliance:latest
  script:
    - gitlab-compliance check -f example-policies -p .gitlab-ci.yml --include-nested --project "$CI_PROJECT_PATH"
```

Depending on your workflow and security policy the pipeline can potentially auto
resolve includes and image updates by passing arg `--fix`
Next: [Usage](../usage/index.md).
