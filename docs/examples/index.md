# Examples

Sample policies for common GitLab CI/CD compliance checks. Full files are in the
repository under
[`examples/example-policies/security/`](https://github.com/MaturityBuilder/gitlab-compliance/tree/main/examples/example-policies/security).

## Workflow badges

Each example page is tagged with the command or focus area it demonstrates:

<p class="example-badges example-badge-legend">
  <a class="example-badge example-badge--check" href="../usage/reference/check.md">check</a>
  <a class="example-badge example-badge--shell-check" href="../usage/reference/shell-check.md">shell-check</a>
  <a class="example-badge example-badge--supply-chain" href="../usage/reference/check.md#fix-supply-chain">supply-chain</a>
</p>

| Badge | Command / focus | Use when |
| ----- | --------------- | -------- |
| **check** | `gitlab-compliance check` | Gherkin policies against pipeline YAML (and optional API settings) |
| **shell-check** | `gitlab-compliance shell-check` | Packaged standards for `script` / `before_script` / `after_script` |
| **supply-chain** | `check` + pinning / `--fix-supply-chain` | Images, includes, components, services, and auto-remediation |

## Quick start

**Compliance (`check`)**

```bash
cp -r examples/example-policies/security/ policies/
gitlab-compliance check -f policies/ -p .gitlab-ci.yml
```

**Shell standards (`shell-check`)**

```bash
gitlab-compliance shell-check -p .gitlab-ci.yml
```

**Supply-chain remediations**

```bash
gitlab-compliance check -f policies/security/ -p .gitlab-ci.yml --fix-supply-chain
```

**Documentation (`generate`)**

```bash
gitlab-compliance generate -i .gitlab-ci.yml --format swagger-markdown -o pipeline-reference.md
```

See [GitLab Docs output example](gitlab-docs-output-example.md) for sample `generate` output.

## check — compliance policies

<p class="example-badges">
  <a class="example-badge example-badge--check" href="../usage/reference/check.md">check</a>
</p>

Gherkin policies run with `gitlab-compliance check`:

- [Execution Policy](execution-policy.md) — jobs without `rules:` or weak guards
- [Template Extends](template-extends.md) — jobs bypassing org templates
- [API Hardening](api-hardening.md) — public logs, unmasked variables
- [Advanced scenarios](advanced-scenarios.md) — Scenario Outline matrices
- [OCI Policy Packs](oci-policy-packs.md) — central policy distribution

## shell-check — CI script standards

<p class="example-badges">
  <a class="example-badge example-badge--shell-check" href="../usage/reference/shell-check.md">shell-check</a>
</p>

Packaged shell standards (not the ShellCheck binary):

- [Shell check](shell-check.md) — quoting, remote pipes, unsafe patterns
- [Shell pinning](shell-pinning.md) — package and download pinning in scripts

## supply-chain — pinning and remediations

<p class="example-badges">
  <a class="example-badge example-badge--supply-chain" href="../usage/reference/check.md#fix-supply-chain">supply-chain</a>
</p>

Pinning policies (via `check`) and optional `--fix-supply-chain` remediations:

- [Image Pinning](image-pinning.md) — floating `latest` tags / digest pins
- [Component Pinning](component-pinning.md) — unpinned `@main` components
- [Fragment Pinning](fragment-pinning.md) — unpinned template `ref:`
- [Include Versions](include-versions.md) — invalid semver or outdated refs
- [Service Pinning](service-pinning.md) — unversioned service images

## Documentation examples

<p class="example-badges">
  <a class="example-badge example-badge--generate" href="../usage/reference/generate.md">generate</a>
</p>

| Topic | Example page |
|-------|----------------|
| Inline YAML (gitstrings) | [Gitstrings inline YAML](gitstrings-inline-yaml.md) |
| Generated pipeline docs | [GitLab Docs output example](gitlab-docs-output-example.md) |

## Consumption patterns

- **Local copy:** Single project, quick start
  - `cp -r examples/example-policies/security/ policies/security/`
- **Shared CI jobs:** Reuse job templates across projects
  - [`example-ci/compliance-jobs.yml`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/examples/example-ci/compliance-jobs.yml)
- **GitHub Actions:** pip or container compliance jobs
  - [`example-github-actions/`](https://github.com/MaturityBuilder/gitlab-compliance/tree/main/examples/example-github-actions)
- **GitLab Functions:** experimental `run:` / `func:` check + generate
  - [`example-gitlab-functions/`](https://github.com/MaturityBuilder/gitlab-compliance/tree/main/examples/example-gitlab-functions)
  - [GitLab Functions guide](../ci-cd/gitlab-functions.md)
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
