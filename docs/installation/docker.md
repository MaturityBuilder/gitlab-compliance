# Docker

![gitlab-compliance](../assets/logo-light.png){ width="280" }

A pre-built Docker image on Python Alpine Linux, published by
[MaturityBuilder](https://github.com/MaturityBuilder/gitlab-compliance).

`gitlab-compliance` is published on [Docker
Hub](https://hub.docker.com/_/gitlab-compliance/) as the `gitlab-compliance`
package.

```bash
docker run -it -v $PWD:/src -w /src -e GITLAB_TOKEN=$GITLAB_TOKEN -e
maturitybuilder/gitlab-compliance check -f example-policies --include-nested
--project <my gitlab project path>
```text

## Audit Pipeline Yaml

```yml
gitlab-compliance:
    image: maturitybuilder/gitlab-compliance
    script:
        - gitlab-compliance check -f example-policies --include-nested --project
          <my gitlab project path>

```text

Depending on your workflow and security policy the pipeline can potentially auto
resolve includes and image updates by passing arg `--fix`
Next: [Usage](../usage/index.md).
