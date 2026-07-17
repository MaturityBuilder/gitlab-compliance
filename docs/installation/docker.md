# Docker

`gitlab-compliance` is available as the
[`maturitybuilder/gitlab-compliance`](https://hub.docker.com/r/maturitybuilder/gitlab-compliance/)
container image.

Use the image when your CI runner already has Docker available or when you want
to pin the CLI by image tag or digest instead of installing from PyPI.

## Run locally

```bash
docker run --rm \
  -v "$PWD:/work" \
  -w /work \
  maturitybuilder/gitlab-compliance:latest \
  check -f policies/security -p .gitlab-ci.yml
```

For API-backed policies, pass the token and project path:

```bash
docker run --rm \
  -v "$PWD:/work" \
  -w /work \
  -e GITLAB_TOKEN \
  maturitybuilder/gitlab-compliance:latest \
  check -f policies/security -p .gitlab-ci.yml \
    --project my-group/my-project --strict
```

## GitLab CI example

```yml
compliance:
  image:
    name: maturitybuilder/gitlab-compliance:latest
    entrypoint: [""]
  stage: test
  script:
    - gitlab-compliance check -f policies/security -p .gitlab-ci.yml
```

Pin `maturitybuilder/gitlab-compliance@sha256:<digest>` for stricter
supply-chain control.

Next: [Usage](../usage/index.md).
