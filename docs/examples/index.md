# Examples

Sample policies for common GitLab CI/CD compliance checks. Full files are in the
repository under
[`examples/example-policies/security/`](https://github.com/MaturityBuilder/gitlab-compliance/tree/main/examples/example-policies/security).

## Quick start

**Compliance**

```bash
cp -r examples/example-policies/security/ policies/
gitlab-compliance check -f policies/ -p .gitlab-ci.yml
```

**Documentation**

```bash
gitlab-compliance generate -i .gitlab-ci.yml \
  --format swagger-markdown \
  --output-file pipeline-reference.md
```

See [Generated pipeline docs output](gitlab-docs-output-example.md) for sample
`generate` output.

## Policy index

- **Image pinning:** Floating `latest` tags
  - [Image Pinning](image-pinning.md)
- **Component pinning:** Unpinned `@main` components
  - [Component Pinning](component-pinning.md)
- **Fragment pinning:** Unpinned template `ref:`
  - [Fragment Pinning](fragment-pinning.md)
- **Include versions:** Invalid semver or outdated refs
  - [Include Versions](include-versions.md)
- **Service pinning:** Unversioned service images
  - [Service Pinning](service-pinning.md)
- **Execution policy:** Jobs without `rules:` or weak guards
  - [Execution Policy](execution-policy.md)
- **Template extends:** Jobs bypassing org templates
  - [Template Extends](template-extends.md)
- **API hardening:** Public logs, unmasked variables
  - [API Hardening](api-hardening.md)
- **Advanced scenarios:** Scenario Outline matrices (variables, component inputs)
  - [Advanced scenarios](advanced-scenarios.md)
- **OCI policy packs:** Central policy distribution
  - [OCI Policy Packs](oci-policy-packs.md)

## Consumption patterns

- **Local copy:** Single project, quick start
  - `cp -r examples/example-policies/security/ policies/security/`
- **Shared CI jobs:** Reuse job templates across projects
  - [`example-ci/compliance-jobs.yml`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/examples/example-ci/compliance-jobs.yml)
- **GitHub Actions:** pip or container compliance jobs
  - [`example-github-actions/`](https://github.com/MaturityBuilder/gitlab-compliance/tree/main/examples/example-github-actions)
- **`include:` from central repo:** Versioned policy + job distribution
  - [GitLab CI/CD](../ci-cd/gitlab-ci.md#include-shared-compliance-jobs)
- **OCI registry:** Immutable policy bundles
  - [OCI Policy Packs](oci-policy-packs.md)
- **Pipeline Execution Policy:** Org-wide injection (GitLab security policies)
  - [Pipeline Execution Policy](../ci-cd/pipeline-execution-policy.md)

Shared job templates:

- **`.compliance:offline`:** YAML-only policies (image pinning, execution
  policy, extends)
- **`.compliance:api`:** API hardening, strict mode
- **`.compliance:codequality`:** GitLab Code Quality MR report
- **`.compliance:oci`:** Policies from OCI registry

## Rollout strategy

1. **Warn-only** — run in CI with `allow_failure: true`
2. **Block** — remove `allow_failure` once baselines are fixed
3. **Central policies** — version policies in a security repo or OCI registry
4. **Org-wide** — inject compliance via Pipeline Execution Policy

See [Using in CI/CD](../ci-cd/index.md) for pipeline integration.
