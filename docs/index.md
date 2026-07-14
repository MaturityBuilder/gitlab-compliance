---
layout: home
title: Overview
permalink: /
---

# GitLab Compliance

[![PyPI version](https://img.shields.io/pypi/v/gitlab-compliance.svg)](https://pypi.org/project/gitlab-compliance/)
[![Docker image](https://img.shields.io/docker/v/maturitybuilder/gitlab-compliance?label=Docker)](https://hub.docker.com/r/maturitybuilder/gitlab-compliance/)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/LICENSE)

`gitlab-compliance` is a BDD compliance testing and documentation generation
toolkit for GitLab CI/CD pipelines and project settings. It runs readable
Gherkin policies against `.gitlab-ci.yml`, local includes, and optional GitLab
API settings, then reports violations before changes reach protected branches.
It can also generate Markdown, Swagger-style Markdown, or HTML reference
documentation from the same pipeline YAML.

Source code: [MaturityBuilder/gitlab-compliance](https://github.com/MaturityBuilder/gitlab-compliance).

![Terminal demo of gitlab-compliance commands](assets/gitlab-compliance-cli-demo.gif)

## Get started

[Get started](installation/index.md){ .md-button .md-button-primary }
[Usage reference](usage/index.md){ .md-button }
[BDD grammar](bdd-reference/index.md){ .md-button }

## What you can do

`gitlab-compliance` supports these workflows from the same pipeline YAML:

| Workflow | Command | What it does |
| -------- | ------- | ------------ |
| **Compliance** | [`check`](usage/reference/check.md) | Run Gherkin policies against `.gitlab-ci.yml` (and optional GitLab API settings) |
| **Pipeline docs** | [`generate`](usage/reference/generate.md) | Build Markdown, Swagger-style Markdown, or HTML reference docs from `.gitlab-ci.yml` |
| **Template docs** | [`document gitstrings`](usage/reference/document-gitstrings.md) | Render decorated CI YAML snippets into README tables |
| **Policy catalogs** | [`policies doc`](usage/reference/policies-doc.md) | Generate searchable Markdown or HTML catalogs from policy metadata |
| **Policy packs** | [`policies push`](usage/reference/policies-push.md) / [`policies pull`](usage/reference/policies-pull.md) | Publish and consume compliance policy bundles through OCI registries |

```bash
pip install gitlab-compliance

# Validate pipeline configuration against policies
gitlab-compliance check -f policies/ -p .gitlab-ci.yml

# Generate pipeline documentation (filter and group output as needed)
gitlab-compliance generate -i .gitlab-ci.yml --format swagger-markdown -o pipeline-reference.md
gitlab-compliance generate -i .gitlab-ci.yml --exclude variables,image --group-by stage
```

See [Usage](usage/index.md) for compliance options and [Generate pipeline
documentation](usage/reference/generate.md) for output formats, `--exclude`,
and `--group-by`.

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
- **documentation:** Generate Markdown, Swagger-style Markdown, or HTML
  reference docs from `.gitlab-ci.yml`

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
