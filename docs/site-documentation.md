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

Produce a static site for inspection:

```bash
mkdocs build --strict
```

The HTML output is written to `public/` (GitLab Pages and GitHub Pages both expect this directory in CI).

### Link rules (`--strict`)

MkDocs only validates links to files under `docs/`. Link to repository paths outside that folder with full URLs (for example `example-policies/` on GitHub), not `../` relative paths.

## GitLab CI/CD

| Job | Stage | When | Purpose |
| --- | --- | --- | --- |
| `docs:review` | `build` | Merge requests and default branch | `mkdocs build --strict`; upload `public/` artifact for review |
| `pages` | `publish` | Default branch only | Build and deploy; GitLab Pages serves `public/` |

Download the **`docs:review`** job artifact on merge requests to preview HTML locally (open `public/index.html`).

PyPI release jobs (`publish` on tags) are unchanged and independent of the documentation site.

## GitHub Actions

Workflow: [`.github/workflows/mkdocs-gh-pages.yml`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/.github/workflows/mkdocs-gh-pages.yml).

| Job | When | Purpose |
| --- | --- | --- |
| `review` | Pull requests to `main` / `master` | `mkdocs build --strict`; upload `mkdocs-preview` artifact |
| `build` | Push to `main` / `master` | Build site for production |
| `deploy` | After `build` on push | Deploy `public/` to GitHub Pages |

Enable **Settings → Pages → Build and deployment → GitHub Actions** if the site does not appear after the first successful production deploy.

On pull requests, open the **review** job and download the **mkdocs-preview** artifact to inspect the built site.

## Adding pages

1. Add or edit Markdown under `docs/`.
2. Register the page in the `nav` section of `mkdocs.yml`.
3. Run `mkdocs build --strict` locally before opening a merge request.
