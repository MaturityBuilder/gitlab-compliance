# GitHub Actions (replaces GitLab CI)

## Workflows

| Workflow | File | Purpose |
| -------- | ---- | ------- |
| CI | `ci.yml` | MegaLinter (non-blocking), pytest, `poetry build`, smoke-test `gitlab-docs` |
| Publish to PyPI | `pypi-publish.yml` | Trusted publishing to PyPI / TestPyPI |
| Docker | `docker.yml` | Build image (requires `dist/` from Poetry) and push to `ghcr.io` |

## PyPI trusted publishing (required once)

1. On [pypi.org](https://pypi.org) → your **gitlab-docs** project → **Publishing** → **Add a new pending publisher**.
2. Choose **GitHub** as the publisher.
3. Set:
   - **Owner**: `MaturityBuilder` (or your org/user)
   - **Repository**: `gitlab-docs`
   - **Workflow name**: `pypi-publish.yml`
   - **Environment name**: `pypi`
4. Create a matching GitHub **environment** named `pypi` under **Settings → Environments** (optional but recommended for approval gates).

Repeat for [test.pypi.org](https://test.pypi.org) with environment name `testpypi` if you use manual TestPyPI publishes.

No long-lived `PYPI_API_TOKEN` secret is required when trusted publishing is configured.

## Triggers

- **CI**: every branch push (except tags) and pull requests.
- **PyPI**: push to `main`, `master`, or `f-code-for-includes-docs`; version tags `v*`; GitHub Releases; manual **workflow_dispatch**.
- **Docker**: same branches/tags as PyPI, plus manual dispatch.

## Version bumps

On branch pushes (not tags), `pypi-publish.yml` runs `poetry version patch` before building, similar to the previous GitLab release job. Tag and release publishes use the version already declared in `pyproject.toml`.
