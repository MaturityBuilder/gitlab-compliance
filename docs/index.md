# GitLab Compliance

![gitlab-compliance by MaturityBuilder](assets/logo-wordmark.png)

`gitlab-compliance` is a lightweight, security- and compliance-focused test
framework for GitLab CI/CD. It runs readable Gherkin policies against
`.gitlab-ci.yml`, resolved local includes, and optional GitLab API settings. The
same CLI can also generate Markdown, Swagger-style Markdown, or HTML reference
documentation for your pipeline.

[Get started](installation/index.md){ .md-button .md-button--primary }
[Usage reference](usage/index.md){ .md-button }
[BDD grammar](bdd-reference/index.md){ .md-button }

BDD compliance testing for GitLab CI/CD pipelines and project settings.
{: .mb-tagline }

![Terminal demo showing gitlab-compliance check and generate commands](assets/gitlab-compliance-terminal-demo.gif){ .mb-demo }

## Why teams use it

| Capability | How it helps |
| ---------- | ------------ |
| Pipeline policy checks | Block risky images, unpinned includes, missing rules, and non-standard jobs before merge |
| API-backed policies | Check project, group, and variable settings when GitLab API context is available |
| Policy packs | Keep reusable `.feature` files locally, in shared repos, or in OCI registries |
| Documentation generation | Create pipeline references that show jobs, variables, includes, rules, and selected attributes |

The policy model follows the same BDD style as
[terraform-compliance](https://terraform-compliance.com/) uses for Terraform
plans. Source code:
[MaturityBuilder/gitlab-compliance](https://github.com/MaturityBuilder/gitlab-compliance).

## Get started

`gitlab-compliance` supports two core workflows from the same pipeline YAML:

| Workflow | Command | What it does |
| -------- | ------- | ------------ |
| **Compliance** | [`check`](usage/reference/check.md) | Run Gherkin policies against `.gitlab-ci.yml` (and optional GitLab API settings) |
| **Documentation** | [`generate`](usage/reference/generate.md) | Build Markdown, swagger-markdown, or HTML reference docs from `.gitlab-ci.yml` |

```bash
pip install gitlab-compliance

# Validate pipeline configuration against policies
gitlab-compliance check -f policies/security/ -p .gitlab-ci.yml

# Generate pipeline documentation (filter and group output as needed)
gitlab-compliance generate -i .gitlab-ci.yml --format swagger-markdown -o pipeline-reference.md
gitlab-compliance generate -i .gitlab-ci.yml --exclude variables,image --group-by stage
```

See [Usage](usage/index.md) for compliance options and [Generate pipeline documentation](usage/reference/generate.md) for output formats, `--exclude`, and `--group-by`.

## Common workflows

| Workflow | Example |
| -------- | ------- |
| Local policy directory | `gitlab-compliance check -f policies/security/ -p .gitlab-ci.yml` |
| OCI policy pack | `gitlab-compliance check -f oci://registry.example.com/org/gitlab-ci-policies:1.0.0 -p .gitlab-ci.yml --update` |
| Markdown report | `gitlab-compliance check -f policies/security/ -p .gitlab-ci.yml --format markdown -o COMPLIANCE-REPORT.md` |
| Pipeline reference | `gitlab-compliance generate -i .gitlab-ci.yml --format swagger-markdown -o pipeline-reference.md` |

## Product strengths

### Compliance as readable tests

Policies are Gherkin scenarios that developers, platform engineers, and security
teams can review together.

### Pre-merge feedback

Run checks in merge requests, local hooks, GitLab CI/CD, or GitHub Actions before
configuration reaches protected branches.

### Portable policy distribution

Keep policy packs in the application repo, a central compliance repo, or an OCI
registry.

### Documentation from source

Generate reference docs from real `.gitlab-ci.yml` content so pipeline docs stay
close to the configuration they describe.

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
