---
layout: home
title: Overview
permalink: /
---
# GitLab Compliance

[![PyPI version](https://img.shields.io/pypi/v/gitlab-compliance.svg)](https://pypi.org/project/gitlab-compliance/)
[![Docker image](https://img.shields.io/docker/v/maturitybuilder/gitlab-compliance?label=Docker)](https://hub.docker.com/r/maturitybuilder/gitlab-compliance/)
[![Repository](https://img.shields.io/badge/GitHub-MaturityBuilder%2Fgitlab--compliance-24292f)](https://github.com/MaturityBuilder/gitlab-compliance)

`gitlab-compliance` is a Python CLI for two common GitLab CI/CD jobs:

- **Compliance checks:** Run readable Gherkin policies against `.gitlab-ci.yml`,
  resolved local includes, and optional GitLab API settings.
- **Pipeline documentation:** Generate Markdown, swagger-style Markdown, or HTML
  reference documentation from the same pipeline YAML.

![Animated terminal demo of gitlab-compliance commands](assets/gitlab-compliance-cli-demo.gif)

## Get started

[Get started](installation/index.md){ .md-button .md-button-primary }
[Usage reference](usage/index.md){ .md-button }
[BDD grammar](bdd-reference/index.md){ .md-button }

`gitlab-compliance` supports two core workflows from the same pipeline YAML:

| Workflow | Command | What it does |
| -------- | ------- | ------------ |
| **Compliance** | [`check`](usage/reference/check.md) | Run Gherkin policies against `.gitlab-ci.yml` (and optional GitLab API settings) |
| **Documentation** | [`generate`](usage/reference/generate.md) | Build Markdown, swagger-markdown, or HTML reference docs from `.gitlab-ci.yml` |
| **Policy packs** | [`policies`](usage/reference/policies.md) | Catalog, pull, and push policy bundles, including OCI registries |
| **Inline docs** | [`document gitstrings`](usage/reference/document-gitstrings.md) | Render decorated YAML snippets into marker-delimited Markdown tables |

```bash
pip install gitlab-compliance

# Validate pipeline configuration against policies
gitlab-compliance check -f policies/ -p .gitlab-ci.yml

# Generate pipeline documentation (filter and group output as needed)
gitlab-compliance generate -i .gitlab-ci.yml --format swagger-markdown -o pipeline-reference.md
gitlab-compliance generate -i .gitlab-ci.yml --exclude variables,image --group-by stage
```

See [Usage](usage/index.md) for compliance options and [Generate pipeline
documentation](usage/reference/generate.md) for output formats, `--exclude`, and
`--group-by`.

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

## Command map

| Need | Start here |
| ---- | ---------- |
| Gate merge requests with local policies | [`check`](usage/reference/check.md) |
| Publish a GitLab Code Quality report | [`check --format codequality`](usage/reference/check.md) |
| Generate pipeline reference documentation | [`generate`](usage/reference/generate.md) |
| Document decorated YAML snippets | [`document gitstrings`](usage/gitstrings.md) |
| Share policies through an OCI registry | [`policies push`](usage/reference/policies-push.md) and [`policies pull`](usage/reference/policies-pull.md) |
| Generate a policy catalog from metadata | [`policies doc`](usage/reference/policies-doc.md) |

## Supporting / Requirements

- **Python:** 3.12 (see [Installing via pip](installation/pip.md))
- **Pipeline file:** `.gitlab-ci.yml` or another path passed with `-p`
- **API checks (optional):** GitLab token plus `--project` or `--group` for
  settings and CI variable policies

Full CLI options: [Usage](usage/index.md). Step grammar: [BDD
Reference](bdd-reference/index.md).

## How can you support the project?

Contributions are welcome. See [Contributing](contributing.md) and the source
repository at
[MaturityBuilder/gitlab-compliance](https://github.com/MaturityBuilder/gitlab-compliance).
