---
layout: home
title: Overview
permalink: /
---
# GitLab Compliance

[![PyPI version](https://img.shields.io/pypi/v/gitlab-compliance.svg)](https://pypi.org/project/gitlab-compliance/)
[![Docker image](https://img.shields.io/docker/v/maturitybuilder/gitlab-compliance?label=Docker)](https://hub.docker.com/r/maturitybuilder/gitlab-compliance/)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](installation/pip.md)

`gitlab-compliance` is a Python CLI for BDD compliance testing and pipeline
documentation. It validates GitLab CI/CD YAML with readable Gherkin policies,
optionally checks GitLab project or group settings through the API, and generates
Markdown, swagger-markdown, or HTML documentation from `.gitlab-ci.yml`.

Source code:
[MaturityBuilder/gitlab-compliance](https://github.com/MaturityBuilder/gitlab-compliance).

## Get started
[Get started](installation/index.md){ .md-button .md-button-primary }
[Usage reference](usage/index.md){ .md-button }
[Examples](examples/index.md){ .md-button }
[BDD grammar](bdd-reference/index.md){ .md-button }

`gitlab-compliance` supports two core workflows from the same pipeline YAML:

| Workflow | Command | What it does |
| -------- | ------- | ------------ |
| **Compliance** | [`check`](usage/reference/check.md) | Run Gherkin policies against `.gitlab-ci.yml` (and optional GitLab API settings) |
| **Documentation** | [`generate`](usage/reference/generate.md) | Build Markdown, swagger-markdown, or HTML reference docs from `.gitlab-ci.yml` |

## See it in action

![Terminal demo showing gitlab-compliance check and generate commands](assets/gitlab-compliance-cli-demo.gif)

```bash
pip install gitlab-compliance

# Validate pipeline configuration against policies
gitlab-compliance check -f policies/ -p .gitlab-ci.yml

# Generate pipeline documentation (filter and group output as needed)
gitlab-compliance generate -i .gitlab-ci.yml --format swagger-markdown -o pipeline-reference.md
gitlab-compliance generate -i .gitlab-ci.yml --exclude variables,container_images --group-by stage
```

See [Usage](usage/index.md) for compliance options and [Generate pipeline documentation](usage/reference/generate.md) for output formats, `--exclude`, and `--group-by`.

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

## Idea

`gitlab-compliance` focuses on [negative
testing](https://en.wikipedia.org/wiki/Negative_testing) — catching
misconfigurations and policy violations — rather than proving that a job runs
successfully end to end.

GitLab CI pipelines are defined in YAML that composes jobs, includes, variables,
and workflow rules. What was missing is a lightweight way to assert that this
configuration follows organizational standards before merge. GitLab offers
native compliance features in higher tiers; `gitlab-compliance` provides an
open, portable alternative inspired by
[terraform-compliance](https://terraform-compliance.com/) and
[Conftest](https://www.conftest.dev/).

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

## Supporting / Requirements

- **Python:** 3.12 (see [Installing via pip](installation/pip.md))
- **Pipeline file:** `.gitlab-ci.yml` or another path passed with `-p`
- **API checks (optional):** GitLab token plus `--project` or `--group` for
  settings and CI variable policies

Full CLI options: [Usage](usage/index.md). Step grammar: [BDD
Reference](bdd-reference/index.md).

## How can you support the project?

Contributions are welcome — see [Contributing](contributing.md).
