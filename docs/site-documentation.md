# Site build and publish

Developer documentation for **GitLab Compliance** is built with [MkDocs](https://www.mkdocs.org/) and the [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) theme. Site configuration is in [`mkdocs.yml` on GitHub](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/mkdocs.yml) at the repository root.

## Local development

Install documentation dependencies (Poetry `docs` group), then serve or build:

```bash
poetry install --with docs
poetry run mkdocs serve
```

If your `poetry.lock` does not yet include the `docs` group, install MkDocs directly:

```bash
pip install "mkdocs>=1.6" "mkdocs-material>=9.6"
mkdocs serve
```

Open the URL printed in the terminal (default `http://127.0.0.1:8000`). Edit files under `docs/`; the preview reloads automatically.

The **table of contents** (heading tree on the right) appears when the browser window is wide enough (~1220px+). On narrower viewports, open the page menu (top right) to see **Table of contents**. Pages need `##` headings or lower — the page `#` title is not listed in the TOC.

Produce a static site for inspection:

```bash
mkdocs build --strict
```

The HTML output is written to `public/` (GitLab Pages and GitHub Pages both expect this directory in CI).

### Link rules (`--strict`)

MkDocs only validates links to files under `docs/`. Link to repository paths outside that folder with full URLs (for example `examples/example-policies/` on GitHub), not `../` relative paths.

## GitLab CI/CD

| Job | Stage | When | Purpose |
| --- | --- | --- | --- |
| `docs:review` | `build` | Merge requests and default branch | `mkdocs build --strict`; upload `public/` artifact for review |
| `pages` | `publish` | Default branch only | Build and deploy; GitLab Pages serves `public/` |

Download the **`docs:review`** job artifact on merge requests to preview HTML locally (open `public/index.html`).

PyPI release jobs (`publish` on tags) are unchanged and independent of the documentation site.

## GitHub Actions

| Workflow | When | Purpose |
| --- | --- | --- |
| [`tests.yml`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/.github/workflows/tests.yml) | PR + push | behave, pytest, coverage |
| [`pre-commit.yml`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/.github/workflows/pre-commit.yml) | PR + push | pre-commit hooks |
| [`danger.yml`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/.github/workflows/danger.yml) | PR | Danger PR review |
| [`docker.yml`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/.github/workflows/docker.yml) | PR + push | Build, Trivy scan, Docker Hub publish |
| [`mkdocs-gh-pages.yml`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/.github/workflows/mkdocs-gh-pages.yml) | PR + push | MkDocs build and GitHub Pages |

See [GitHub Actions CI/CD](ci-cd/github-actions.md) for consumer examples (pip vs container) and Docker Hub publish setup.

### Documentation site

| Job | When | Purpose |
| --- | --- | --- |
| `review` | Pull requests to `main` / `master` | `mkdocs build --strict`; upload `mkdocs-preview` artifact |
| `build` | Push to `main` / `master` | Build site for production |
| `deploy` | After `build` on push | Deploy `public/` to GitHub Pages |

Enable **Settings → Pages → Build and deployment → GitHub Actions** if the site does not appear after the first successful production deploy.

On pull requests, open the **review** job and download the **mkdocs-preview** artifact to inspect the built site.

## Site structure

Navigation mirrors [terraform-compliance.com](https://terraform-compliance.com/):

| Section | Purpose |
| --- | --- |
| Overview | Product introduction and BDD example |
| Installation | pip |
| Usage | CLI reference, parameters, environment variables |
| BDD Reference | Gherkin step grammar |
| Examples | Security policy patterns |
| Using in CI/CD | GitLab CI, GitHub Actions, Pipeline Execution Policy |
| Contributing | Development and docs workflow |

## Adding pages

1. Add or edit Markdown under `docs/` (use subfolders for sections, e.g. `docs/examples/`).
2. Register the page in the `nav` section of `mkdocs.yml`.
3. Run `mkdocs build --strict` locally before opening a merge request.
