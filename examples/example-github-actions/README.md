# GitHub Actions examples

Copy or adapt these workflows into `.github/workflows/` in your repository.

- **[`compliance-pip.yml`](compliance-pip.yml):**
  - `pip install gitlab-compliance`
  - Fastest setup, no Docker required on the runner
- **[`compliance-container.yml`](compliance-container.yml):**
  - `docker run maturitybuilder/gitlab-compliance`
  - Pin an immutable image digest; no Python setup on the runner

## Prerequisites

1. Copy policies into your repo (for example from
[`examples/example-policies/security/`](../example-policies/security/)):

   ```bash
   cp -r examples/example-policies/security policies/security
   ```

2. Point `-p` / `--pipeline` at your pipeline file (`.gitlab-ci.yml`,
`.github/workflows/ci.yml`, etc.).

## Pip vs container

- **Runner requirements:** Python 3.12 — Docker only
- **Version pinning:**
  - `pip install gitlab-compliance==1.0.6`
  - Image tag or `@sha256:` digest
- **Cold start:** pip download on each job — image pull (cacheable)
- **Best for:** Small repos, quick adoption — Strict supply-chain controls

## Related documentation

- [Using in CI/CD](../../docs/ci-cd/index.md) — GitLab CI, Functions, and
  pipeline execution policy (published site)
- [GitLab CI/CD guide](../../docs/ci-cd/gitlab-ci.md) — shared job templates for
  GitLab

Maintainer workflow notes for this repository live under [`.github/`](../../.github/)
and are not published on GitHub Pages.
