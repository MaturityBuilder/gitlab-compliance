# Pipeline documentation output example

This page shows a concise excerpt from the `generate` command.

Run the command from the repository root:

```bash
gitlab-compliance generate \
  -i examples/sample-files/.gitlab-ci.yml \
  --format swagger-markdown \
  --exclude inputs,variables,workflow \
  -o pipeline-reference.md
```

Generated output starts with a table of contents, then renders includes and jobs
as Markdown tables:

```markdown
# GitLab pipeline reference — `examples/sample-files/.gitlab-ci.yml`

- **Config file:** `examples/sample-files/.gitlab-ci.yml`
- **Jobs:** 10

## Contents

- [Includes](#includes)
- [Jobs](#jobs) (10)
  - TODO-CHECK
  - GITLEAKS
  - SHELL-CHECK
  - FRAGMENT-VERSION-CHECK
  - .DOCKER.BUILD
  - BUILD
  - PUBLISH

## Includes

| Include Type | Project                             | Version | Valid | File                |
| ------------ | ----------------------------------- | ------- | ----- | ------------------- |
| local        | gitlab-ci/includes_without_keys.yml | n/a     | yes   |                     |
| project      | charlieasmith/a-generic-fragment    | main    | no    | a-fragment-file.yml |
| local        | gitlab-ci/includes_with_keys.yml    | n/a     | yes   |                     |

## Jobs

### JOB · TODO-CHECK

> extends: 1. .todo-check-template · stage: code-quality

#### TODO-CHECK · attributes

| Attribute | Value                   |
| --------- | ----------------------- |
| extends   | 1. .todo-check-template |
| stage     | code-quality            |

---

### TEMPLATE · .DOCKER.BUILD

> image: docker · services: ['docker:24.0.5-dind', None]

#### .DOCKER.BUILD · nested attributes

| Attribute | Key             | Value                                                   |
| --------- | --------------- | ------------------------------------------------------- |
| variables | DOCKER_BUILDKIT | 1                                                       |
| variables | DOCKER_DRIVER   | overlay2                                                |
| variables | ECR_URL         | some_aws_account_number.dkr.ecr.eu-west-2.amazonaws.com |
```

Use `--format markdown` when you want marker-delimited output that can update an
existing README, or `--format html` when publishing a standalone static page.
