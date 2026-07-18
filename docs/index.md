# Gitlab Compliance

![PyPI version](https://img.shields.io/pypi/v/gitlab-compliance.svg)
![Docker image](https://img.shields.io/docker/v/maturitybuilder/gitlab-compliance?label=Docker)

`gitlab-compliance` is a Python CLI for BDD compliance testing and pipeline
documentation. It runs readable Gherkin policies against `.gitlab-ci.yml`,
optionally enriches checks with the GitLab API, and can generate Markdown or
HTML reference documentation from the same pipeline file.

Source:
[MaturityBuilder/gitlab-compliance](https://github.com/MaturityBuilder/gitlab-compliance).

## Start here

| Goal | Guide |
| ---- | ----- |
| Install locally or in CI | [Installation](installation/index.md) |
| Run compliance checks | [Usage](usage/index.md) |
| Write Gherkin policies | [BDD Reference](bdd-reference/index.md) |
| Copy examples | [Examples](examples/index.md) |
| Add to CI/CD | [Using in CI/CD](ci-cd/index.md) |

## What it does

`gitlab-compliance` supports two primary workflows from one pipeline YAML:

| Workflow | Command | What it does |
| -------- | ------- | ------------ |
| Compliance | [`check`](usage/reference/check.md) | Run Gherkin policies against `.gitlab-ci.yml` and optional GitLab API settings |
| Documentation | [`generate`](usage/reference/generate.md) | Build Markdown, swagger-markdown, or HTML reference docs from `.gitlab-ci.yml` |

![CLI demo](assets/gitlab-compliance-cli-demo.gif)

## Quick start

```bash
pip install gitlab-compliance

# Validate pipeline configuration against policies
gitlab-compliance check -f policies/ -p .gitlab-ci.yml

# Generate pipeline documentation
gitlab-compliance generate -i .gitlab-ci.yml --format swagger-markdown -o pipeline-reference.md
```

Use [Additional Parameters](usage/additional-parameters.md) for `--strict`,
`--with-builtin`, OCI policy packs, `--exclude`, and `--group-by`.

## Why teams use it

- **compliance:** Ensure pipeline YAML and project settings follow your security
  standards and custom policies
- **behaviour driven development:** Policies are readable Gherkin scenarios that
  developers and security teams share
- **portable:** Install from `pip`. See [Installation](installation/index.md)
- **pre-merge:** Validate configuration before changes land on protected
  branches
- **YAML and API:** Offline checks against pipeline files; optional GitLab API
  checks for project settings and CI variables
- **easy to integrate:** Run in GitLab CI or local git hooks
- **segregation of duty:** Keep policy packs in a separate repository or OCI
  registry
- **documentation:** Generate Markdown or HTML reference docs from
  `.gitlab-ci.yml`

## Policy idea

`gitlab-compliance` focuses on [negative
testing](https://en.wikipedia.org/wiki/Negative_testing) — catching
misconfigurations and policy violations — rather than proving that a job runs
successfully end to end.

For example, a policy might require that no job uses a floating `latest` image
tag:

```gherkin
if a job defines an image, it must not use the :latest tag
```

translates into:

```gherkin
Given I have any job defined
When it has image
Then its image must not match ":latest$"
```

The `image` value comes from your pipeline YAML:

```yaml
scan:
  image: python:3.12
build:
  image: docker:latest   # violates the policy above
```

In CI, this scenario runs against `.gitlab-ci.yml` (and resolved local includes)
so merge requests cannot introduce violations.

See [Examples](examples/index.md) for more sample use cases.

## Requirements

- **Python:** 3.12 (see [Installing via pip](installation/pip.md))
- **Pipeline file:** `.gitlab-ci.yml` or another path passed with `-p`
- **API checks (optional):** GitLab token plus `--project` or `--group` for
  settings and CI variable policies

Full CLI options: [Usage](usage/index.md). Step grammar: [BDD
Reference](bdd-reference/index.md).

## Contributing

Contributions are welcome — see [Contributing](contributing.md).
