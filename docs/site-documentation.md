# Site build and publish

Developer documentation for **gitlab-compliance** (by
[MaturityBuilder](https://github.com/MaturityBuilder/gitlab-compliance)) is built with
[Zensical](https://zensical.org/). Site configuration is in [`mkdocs.yml` on
GitHub](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/mkdocs.yml)
at the repository root (Zensical reads this format natively).

## Local development

Install documentation dependencies (Poetry `docs` group), then serve or build:

```bash
poetry install --with docs
poetry run zensical serve
```

If your `poetry.lock` does not yet include the `docs` group, install Zensical
directly:

```bash
pip install "zensical>=0.0.47"
zensical serve
```

Open the URL printed in the terminal (default `http://127.0.0.1:8000`). Edit
files under `docs/`; the preview reloads automatically.

The **table of contents** (heading tree on the right) appears when the browser
window is wide enough (~1220px+). On narrower viewports, open the page menu (top
right) to see **Table of contents**. Pages need `##` headings or lower — the
page `#` title is not listed in the TOC.

Produce a static site for inspection:

```bash
zensical build --strict
```

The HTML output is written to `public/` (GitLab Pages and GitHub Pages both
expect this directory in CI).

### Link rules (`--strict`)

Zensical only validates links to files under `docs/`. Link to repository paths
outside that folder with full URLs (for example `examples/example-policies/` on
GitHub), not `../` relative paths.

## GitLab CI/CD

- **`docs:review`:** `build`
  - Merge requests and default branch
  - `zensical build --strict`; upload `public/` artifact for review
- **`pages`:** `publish`
  - Default branch only
  - Build and deploy; GitLab Pages serves `public/`

Download the **`docs:review`** job artifact on merge requests to preview HTML
locally (open `public/index.html`).

PyPI and Docker Hub publish (on semver tags via
[`release.yml`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/.github/workflows/release.yml))
are independent of the documentation site.

## GitHub Actions

- **[`tests.yml`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/.github/workflows/tests.yml):**
  PR + push
  - behave, pytest, coverage
- **[`pre-commit.yml`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/.github/workflows/pre-commit.yml):**
  PR + push
  - pre-commit hooks
- **[`danger.yml`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/.github/workflows/danger.yml):**
  PR
  - Danger PR review
- **[`docker.yml`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/.github/workflows/docker.yml):**
  PR + push
  - Build, Trivy scan, smoke test (no push)
- **[`release.yml`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/.github/workflows/release.yml):**
  push `main` / tags `v*`
  - release-please; PyPI + Docker Hub on tags
- **[`zensical-gh-pages.yml`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/.github/workflows/zensical-gh-pages.yml):**
  PR + push
  - Zensical build and GitHub Pages

See [GitHub Actions CI/CD](ci-cd/github-actions.md) for consumer examples (pip
vs container) and Docker Hub publish setup.

### Documentation site

- **`review`:** Pull requests to `main` / `master`
  - `zensical build --strict`; upload `docs-preview` artifact
- **`build`:** Push to `main` / `master`
  - Build site for production
- **`deploy`:** After `build` on push
  - Deploy `public/` to GitHub Pages

Enable **Settings → Pages → Build and deployment → GitHub Actions** if the site
does not appear after the first successful production deploy.

On pull requests, open the **review** job and download the **docs-preview**
artifact to inspect the built site.

## Site structure

Navigation mirrors
[terraform-compliance.com](https://terraform-compliance.com/):

| Section        | Purpose                                              |
| -------------- | ---------------------------------------------------- |
| Overview       | Product introduction and BDD example                 |
| Installation   | pip                                                  |
| Usage          | CLI overview, command pages, demos, env vars         |
| BDD Reference  | Gherkin step grammar                                 |
| Examples       | Security policy patterns                             |
| Using in CI/CD | GitLab CI, GitHub Actions, Pipeline Execution Policy |
| Contributing   | Development and docs workflow                        |

## CLI demo GIFs

Terminal demos live under [`docs/demos/`](demos/README.md) (VHS `.tape` sources,
committed GIFs, and HTML/MR screenshots). They are embedded on Usage command
pages. Record offline demos from the repo root:

```bash
bash scripts/record-demos.sh offline
```

Live GitLab/OCI demos need sandbox credentials — see the
[demos README](demos/README.md). The GitHub Actions `demos-offline` job
validates offline tapes and checks that expected GIF/screenshot files exist.

## Adding pages

1. Add or edit Markdown under `docs/` (use subfolders for sections, e.g.
`docs/examples/`).
2. Register the page in the `nav` section of `mkdocs.yml`.
3. Run `zensical build --strict` locally before opening a merge request.
