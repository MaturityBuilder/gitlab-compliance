# gitlab-compliance

**BDD compliance testing and documentation generation for GitLab CI/CD
pipelines.**

[Get started](installation/index.md){ .md-button .md-button--primary }
[Usage reference](usage/index.md){ .md-button }
[BDD grammar](bdd-reference/index.md){ .md-button }
[Examples](examples/index.md){ .md-button }

`gitlab-compliance` is a Python 3.12 CLI from
[MaturityBuilder](https://github.com/MaturityBuilder/gitlab-compliance). It
runs readable Gherkin policies against `.gitlab-ci.yml`, can enrich checks with
GitLab API settings, and can generate Markdown, Swagger-style Markdown, or HTML
pipeline documentation from the same YAML file.

![gitlab-compliance CLI demo](assets/gitlab-compliance-cli-demo.gif)

## What you can do

| Workflow | Command | Result |
| -------- | ------- | ------ |
| **Check compliance** | [`gitlab-compliance check`](usage/reference/check.md) | Fail on policy violations in pipeline YAML or GitLab settings |
| **Generate docs** | [`gitlab-compliance generate`](usage/reference/generate.md) | Produce Markdown, `swagger-markdown`, or HTML pipeline reference docs |
| **Publish policy packs** | [`gitlab-compliance policies`](usage/reference/policies.md) | Document, push, and pull reusable policy bundles |

## Quick start

Install the CLI, copy example policies, and run a local check:

```bash
pip install gitlab-compliance
cp -r examples/example-policies/security/ policies/security/
gitlab-compliance check -f policies/security/ -p .gitlab-ci.yml
```

Generate a Markdown reference for the same pipeline:

```bash
gitlab-compliance generate \
  -i .gitlab-ci.yml \
  --format swagger-markdown \
  -o pipeline-reference.md
```

Useful next reads:

- [Installation](installation/index.md)
- [Usage](usage/index.md)
- [Command reference](usage/reference/command-reference.md)
- [Using in CI/CD](ci-cd/index.md)

## Policy model

`gitlab-compliance` uses the same behavior-driven style as
[terraform-compliance](https://terraform-compliance.com/): policy files are
Gherkin scenarios that security teams and developers can read together.

For example, this policy blocks jobs that use a floating `latest` image tag:

```gherkin
Given I have any job defined
When it has image
Then its image must not match ":latest$"
```

It evaluates values from your pipeline YAML:

```yaml
scan:
  image: python:3.12

build:
  image: docker:latest
```

Run the scenario before merge so a non-compliant pipeline cannot land on a
protected branch.

## Why teams use it

- **Readable controls:** Write policies as Gherkin, not custom scripts.
- **YAML and API coverage:** Check pipeline structure offline and GitLab project
  settings when a token is available.
- **Portable delivery:** Run from pip, Docker, GitLab CI, GitHub Actions, or an
  OCI-hosted policy pack.
- **Docs from source:** Generate auditable pipeline reference pages from the
  same `.gitlab-ci.yml` you test.
- **Supply-chain fixes:** Use `--fix` to pin supported includes and container
  images when credentials permit it.

## Requirements

- Python 3.12 for local pip/Poetry installs.
- A GitLab CI YAML file, usually `.gitlab-ci.yml`.
- A policy directory or OCI policy reference for `check`.
- Optional `GITLAB_TOKEN` plus `--project` or `--group` for API-backed checks.

Contributions are welcome. See [Contributing](contributing.md) for local setup,
tests, and documentation workflow.
