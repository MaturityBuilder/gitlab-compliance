# Docker

![gitlab-compliance](../assets/logo-light.png)

A pre-built Docker image on Python Alpine Linux, published by
[MaturityBuilder](https://github.com/MaturityBuilder/gitlab-compliance).

`gitlab-compliance` is published on
[Docker Hub](https://hub.docker.com/r/maturitybuilder/gitlab-compliance) as
`maturitybuilder/gitlab-compliance`.

```bash
docker run --rm \
  -v "$PWD:/src" \
  -w /src \
  -e GITLAB_TOKEN \
  maturitybuilder/gitlab-compliance:latest \
  check -f example-policies -p .gitlab-ci.yml \
  --include-nested --project my-group/my-project
```

## Audit pipeline YAML

```yaml
gitlab-compliance:
  image: maturitybuilder/gitlab-compliance:latest
  script:
    - >-
      gitlab-compliance check
      -f example-policies
      -p .gitlab-ci.yml
      --include-nested
      --project my-group/my-project
```

Depending on your workflow and security policy, the pipeline can auto-resolve
includes and image updates by passing `--fix`.

Next: [Usage](../usage/index.md).
