# GitHub Actions

Run **gitlab-compliance** in GitHub Actions to gate pull requests and
default-branch builds. This repository also ships workflows for tests,
documentation, Docker image checks, and tag-gated PyPI and Docker publishing.

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
    - run: gitlab-compliance check -f policies/security -p .gitlab-ci.yml
```

Full example:
[`examples/example-github-actions/compliance-pip.yml`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/examples/example-github-actions/compliance-pip.yml).

### Run via container

```yaml
compliance:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4
    - run: |
        docker run --rm -v "$PWD:/work" -w /work \
          maturitybuilder/gitlab-compliance:latest \
          check -f policies/security -p .gitlab-ci.yml
```

Full example:
[`examples/example-github-actions/compliance-container.yml`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/examples/example-github-actions/compliance-container.yml).

Copy policies first:

```bash
cp -r examples/example-policies/security policies/security
```

## Repository workflows

- **Tests:**
  [`tests.yml`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/.github/workflows/tests.yml)
  - PR + push
  - behave + pytest, 95% coverage
- **Docker:**
  [`docker.yml`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/.github/workflows/docker.yml)
  - PR + push
  - Build, Trivy scan, smoke test
- **Release:**
  [`release.yml`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/.github/workflows/release.yml)
  - push `main` / tags
  - release-please; PyPI + Docker
- **Documentation:**
  [`zensical-gh-pages.yml`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/.github/workflows/zensical-gh-pages.yml)
  - PR + push
  - Zensical build and GitHub Pages

## Pre-commit (local and CI)

Install hooks after cloning:

```bash
poetry install
poetry run pre-commit install
poetry run pre-commit run --all-files
```

Configuration:
[`.pre-commit-config.yaml`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/.pre-commit-config.yaml).

## Release (release-please, PyPI, Docker Hub)

Releases are automated with
[release-please](https://github.com/googleapis/release-please). Configuration
lives in
[`release-please-config.json`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/release-please-config.json)
and
[`.release-please-manifest.json`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/.release-please-manifest.json).

### Release flow

1. Merge conventional commits (`feat:`, `fix:`, `BREAKING CHANGE:`) to `main`.
2. The **release-please** job opens or updates a Release PR (version bump in
`pyproject.toml` and `src/__init__.py`, plus `CHANGELOG.md`).
3. Merge the Release PR — release-please creates a GitHub Release and tag
`vX.Y.Z`.
4. The tag push runs **test**, then **publish-pypi** and **publish-docker** in
parallel.

If CI does not run on release-please PRs, switch the release-please step to a
personal access token (`MY_RELEASE_PLEASE_TOKEN`) per the [release-please-action
credentials
docs](https://github.com/googleapis/release-please-action#github-credentials).

### One-time publish setup

#### PyPI (OIDC trusted publishing)

PyPI publish uses [trusted
publishing](https://docs.pypi.org/trusted-publishers/) (OIDC) — no long-lived
`PYPI_TOKEN` secret is required.

1. On
[PyPI](https://pypi.org/manage/project/gitlab-compliance/settings/publishing/),
add a **trusted publisher** for GitHub Actions:

   | Field | Value |
   |-------|-------|
   | Owner | `MaturityBuilder` |
   | Repository | `gitlab-compliance` |
   | Workflow name | `release.yml` |
   | Environment name | `pypi` |

2. In GitHub **Settings → Environments**, create a **`pypi`** environment
(optional but recommended for deployment protection).

The **publish-pypi** job runs `poetry build`, then uploads with
[`pypa/gh-action-pypi-publish`](https://github.com/pypa/gh-action-pypi-publish)
using `id-token: write`.

#### Docker Hub

Add these in GitHub **Settings → Secrets and variables → Actions**:

- **`DOCKERHUB_USERNAME`:** Variable
  - Docker Hub username or org name (`maturitybuilder`)
- **`DOCKERHUB_TOKEN`:** Secret
  - Docker Hub access token with **Read & Write** scope ([create
    token](https://docs.docker.com/docker-hub/access-tokens/))

Docker publish tags semver releases as `X.Y.Z`, `X.Y`, and `latest` (only on
tagged releases, not on every `main` push). Builds include provenance and SBOM
attestations.

## Docker build and scan

Image: **`maturitybuilder/gitlab-compliance`**

The `build-and-scan` job in
[`docker.yml`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/.github/workflows/docker.yml)
runs on pull requests and pushes to `main` / `master`:

1. Builds from
[`dockerfile`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/dockerfile)
(no push)
2. Runs Trivy filesystem and image scans (`CRITICAL`, `HIGH` severities fail the
job)
3. Uploads image scan SARIF to the Security tab
4. Smoke-tests `gitlab-compliance --help`

Docker Hub push happens only from the **publish-docker** job in
[`release.yml`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/.github/workflows/release.yml)
when a semver tag is created.

## API-backed policies

For GitLab project settings and CI variable checks, pass a token and project
path:

```yaml
- run: |
    gitlab-compliance check \
      -f policies/security \
      -p .gitlab-ci.yml \
      --project my-group/my-project \
      --strict
  env:
    GITLAB_TOKEN: ${{ secrets.GITLAB_TOKEN }}
```

## Related guides

- **[GitLab CI/CD](gitlab-ci.md):** Shared job templates, Code Quality reports
- **[Pipeline Execution Policy](pipeline-execution-policy.md):** Org-wide GitLab
  injection
- **[Examples](../examples/index.md):** Policy patterns and consumption
