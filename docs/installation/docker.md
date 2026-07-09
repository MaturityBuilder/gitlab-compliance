# Docker

![gitlab-compliance](../assets/logo-light.svg){ width="280" }

The published image runs `gitlab-compliance` as its entrypoint, so pass
subcommands such as `check`, `generate`, or `policies` after the image name.

Image repository:
[`maturitybuilder/gitlab-compliance`](https://hub.docker.com/r/maturitybuilder/gitlab-compliance).

## Run a compliance check

```bash
docker run --rm \
  -v "$PWD:/work" \
  -w /work \
  -e GITLAB_TOKEN \
  maturitybuilder/gitlab-compliance:latest \
  check -f policies/security/ -p .gitlab-ci.yml --project my-group/my-project
```

## Generate pipeline documentation

```bash
docker run --rm \
  -v "$PWD:/work" \
  -w /work \
  maturitybuilder/gitlab-compliance:latest \
  generate -i .gitlab-ci.yml --format swagger-markdown -o pipeline-reference.md
```

## GitLab CI example

```yaml
gitlab-compliance:
  image:
    name: maturitybuilder/gitlab-compliance:latest
    entrypoint: [""]
  script:
    - gitlab-compliance check -f policies/security/ -p .gitlab-ci.yml
```

Pin a digest for production runners when your supply-chain policy requires it:

```yaml
image: maturitybuilder/gitlab-compliance@sha256:<digest>
```

Depending on your workflow and security policy, `check --fix` can update stale
include versions and pin images to digests before running assertions.

Next: [Usage](../usage/index.md).
