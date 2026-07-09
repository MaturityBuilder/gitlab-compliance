# gitlab-compliance

![gitlab-compliance by MaturityBuilder](assets/logo-light.png)

`gitlab-compliance` is a lightweight compliance and documentation toolkit for
GitLab CI/CD. It runs readable Gherkin policies against `.gitlab-ci.yml`, can
include GitLab API-backed project or group checks, and can generate pipeline
reference documentation from the same YAML file.

Use it when you need to catch policy drift before merge, document how a pipeline
is assembled, or distribute reusable compliance rules across projects.

| Start here | Purpose |
| ---------- | ------- |
| [Installation](installation/index.md) | Install with pip or run the container image |
| [Usage](usage/index.md) | Run compliance checks and generate pipeline docs |
| [Command reference](usage/reference/command-reference.md) | Review current CLI commands and options |
| [BDD reference](bdd-reference/index.md) | Write policies with supported Gherkin steps |
| [Examples](examples/index.md) | Copy ready-to-adapt policies and CI snippets |

## Get started

`gitlab-compliance` supports these core workflows from the same pipeline YAML:

| Workflow | Command | What it does |
| -------- | ------- | ------------ |
| Compliance | [`check`](usage/reference/check.md) | Runs Gherkin policies against pipeline YAML and optional GitLab API settings |
| Documentation | [`generate`](usage/reference/generate.md) | Builds Markdown, swagger-markdown, or HTML reference docs from pipeline YAML |
| Policy bundles | [`policies`](usage/reference/policies.md) | Builds policy catalogs and moves policy packs to or from OCI registries |

```bash
pip install gitlab-compliance

# Validate pipeline configuration against policies
gitlab-compliance check -f policies/ -p .gitlab-ci.yml

# Generate pipeline documentation (filter and group output as needed)
gitlab-compliance generate -i .gitlab-ci.yml --format swagger-markdown -o pipeline-reference.md
gitlab-compliance generate -i .gitlab-ci.yml --exclude variables,image --group-by stage
```

See [Usage](usage/index.md) for compliance options and
[Generate pipeline documentation](usage/reference/generate.md) for output
formats, `--exclude`, and `--group-by`.

## What it helps with

- **Compliance:** Ensure pipeline YAML and project settings follow your security
  standards and custom policies
- **Behavior-driven development:** Policies are readable Gherkin scenarios that
  developers and security teams share
- **Portable:** Install from `pip` or run the container image. See
  [Installation](installation/index.md)
- **Pre-merge:** Validate configuration before changes land on protected
  branches
- **YAML and API:** Offline checks against pipeline files; optional GitLab API
  checks for project settings and CI variables
- **Easy to integrate:** Run in GitLab CI, GitHub Actions, or local git hooks
- **Segregation of duty:** Keep policy packs in a separate repository or OCI
  registry
- **Documentation:** Generate Markdown or HTML reference docs from
  `.gitlab-ci.yml`

## Idea

`gitlab-compliance` focuses on [negative
testing](https://en.wikipedia.org/wiki/Negative_testing) - catching
misconfigurations and policy violations - rather than proving that a job runs
successfully end-to-end.

GitLab CI pipelines are defined in YAML that composes jobs, includes, variables,
and workflow rules. What was missing is a lightweight way to assert that this
configuration follows organizational standards before merge. GitLab offers
native compliance features in higher tiers. `gitlab-compliance` provides an
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

## Requirements

- **Python:** 3.12 (see [Installing via pip](installation/pip.md))
- **Pipeline file:** `.gitlab-ci.yml` or another path passed with `-p`
- **API checks (optional):** GitLab token plus `--project` or `--group` for
  settings and CI variable policies

Full CLI options: [Usage](usage/index.md). Step grammar: [BDD
Reference](bdd-reference/index.md).

## How can you support the project?

Contributions are welcome - see [Contributing](contributing.md).
