# Docker

A pre-built docker image built on python alpine linux.

`gitlab-compliance` is published on [Docker Hub](https://hub.docker.com/_/gitlab-compliance/) as the `gitlab-compliance` package.

```bash
docker run -it -v $PWD:/src -w /src -e GITLAB_TOKEN=$GITLAB_TOKEN -e  maturitybuilder/gitlab-compliance check -f example-policies --include-nested --project <my gitlab project path>
```

## Audit Pipeline Yaml
```yml
gitlab-compliance:
    image: maturitybuilder/gitlab-compliance
    script:
        - gitlab-compliance check -f example-policies --include-nested --project <my gitlab project path>

```

Depending on your workflow and security policy the pipeline can potentially auto resolve includes and image updates by passing arg `--fix`
Next: [Usage](../usage/index.md).
