# GitHub Actions

Run **gitlab-compliance** in GitHub Actions to gate pull requests and default-branch builds. This repository also ships workflows for pre-commit, Danger PR review, tests, documentation, and Docker publish.

## Quick start (consumer projects)

### Install via pip

```yaml
compliance:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4
    - uses: actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065 # v5
      with:
        python-version: "3.12"
    - run: pip install gitlab-compliance
    - run: gitlab-compliance compliance -f policies/security -p .gitlab-ci.yml
```

Full example: [`examples/example-github-actions/compliance-pip.yml`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/examples/example-github-actions/compliance-pip.yml).

### Run via container

```yaml
compliance:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4
    - run: |
        docker run --rm -v "$PWD:/work" -w /work \
          maturitybuilder/gitlab-compliance:latest \
          compliance -f policies/security -p .gitlab-ci.yml
```

Full example: [`examples/example-github-actions/compliance-container.yml`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/examples/example-github-actions/compliance-container.yml).

Copy policies first:

```bash
cp -r examples/example-policies/security policies/security
```

## Repository workflows

| Workflow | File | When | Purpose |
|----------|------|------|---------|
| Tests | [`.github/workflows/tests.yml`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/.github/workflows/tests.yml) | PR + push | behave + pytest, 70% coverage gate |
| Pre-commit | [`.github/workflows/pre-commit.yml`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/.github/workflows/pre-commit.yml) | PR + push | `pre-commit run --all-files` |
| Danger | [`.github/workflows/danger.yml`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/.github/workflows/danger.yml) | PR | PR review comments via [`dangerfile.py`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/dangerfile.py) |
| Docker | [`.github/workflows/docker.yml`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/.github/workflows/docker.yml) | PR + push | Build, Trivy scan; push on `main` / semver tags |
| Documentation | [`.github/workflows/zensical-gh-pages.yml`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/.github/workflows/zensical-gh-pages.yml) | PR + push | Zensical build and GitHub Pages deploy |

## Pre-commit (local and CI)

Install hooks after cloning:

```bash
poetry install
poetry run pre-commit install
poetry run pre-commit run --all-files
```

Configuration: [`.pre-commit-config.yaml`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/.pre-commit-config.yaml).

## Danger PR review

[`dangerfile.py`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/dangerfile.py) warns on:

- Very large PRs
- `src/` changes without `tests/` or `docs/` updates
- CI file changes (links to this guide)
- Non-conventional PR titles (informational)

Enable **Settings → Actions → General → Workflow permissions → Read and write** so `GITHUB_TOKEN` can post PR comments.

## Docker build, scan, and publish

Image: **`maturitybuilder/gitlab-compliance`**

### Pull requests and branches

The `build-and-scan` job:

1. Builds from [`dockerfile`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/dockerfile) (no push)
2. Runs Trivy filesystem and image scans (`CRITICAL`, `HIGH` severities fail the job)
3. Uploads image scan SARIF to the Security tab
4. Smoke-tests `gitlab-compliance --help`

### Publish (main, master, and `v*.*.*` tags)

The `publish` job pushes to Docker Hub using a **personal access token** (PAT).

#### One-time Docker Hub setup

1. In [Docker Hub](https://hub.docker.com), create an [access token](https://docs.docker.com/docker-hub/access-tokens/) with **Read & Write** scope for the **maturitybuilder** namespace.
2. In GitHub **Settings → Secrets and variables → Actions**, add:

   | Name | Type | Value |
   |------|------|-------|
   | `DOCKERHUB_USERNAME` | Variable | Docker Hub username or org name (`maturitybuilder`) |
   | `DOCKERHUB_TOKEN` | Secret | Docker Hub access token (not your account password) |

The workflow logs in with:

```yaml
- uses: docker/login-action@af1e73f918a031802d376d3c8bbc3fe56130a9b0 # v4
  with:
    username: ${{ vars.DOCKERHUB_USERNAME }}
    password: ${{ secrets.DOCKERHUB_TOKEN }}
```

Tags include `latest` (default branch), `sha-<short>`, branch name, and semver tags when you push `v*.*.*` git tags. Builds include provenance and SBOM attestations.

## API-backed policies

For GitLab project settings and CI variable checks, pass a token and project path:

```yaml
- run: |
    gitlab-compliance compliance \
      -f policies/security \
      -p .gitlab-ci.yml \
      --project my-group/my-project \
      --strict
  env:
    GITLAB_TOKEN: ${{ secrets.GITLAB_TOKEN }}
```

## Related guides

| Guide | Purpose |
|-------|---------|
| [GitLab CI/CD](gitlab-ci.md) | Shared job templates, Code Quality reports |
| [Pipeline Execution Policy](pipeline-execution-policy.md) | Org-wide GitLab injection |
| [Examples](../examples/index.md) | Policy patterns and consumption |
