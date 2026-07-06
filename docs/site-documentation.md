# Site build and publish

Developer documentation for this project is built with [MkDocs](https://www.mkdocs.org/) and the [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) theme. Configuration lives in [`mkdocs.yml`](../mkdocs.yml) at the repository root.

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
poetry run mkdocs build --strict
```

The HTML output is written to `public/` (GitLab Pages and GitHub Pages both expect this directory in CI).

## GitLab CI/CD

The pipeline builds and publishes the site on the default branch:

| Job | Stage | When | Purpose |
| --- | --- | --- | --- |
| `docs:build` | `build` | Merge requests and default branch | `mkdocs build --strict` (artifact for review) |
| `pages` | `publish` | Default branch only | Same build; GitLab Pages serves `public/` |

PyPI release jobs (`publish` on tags) are unchanged and independent of the documentation site.

## GitHub Actions

The **Deploy MkDocs to GitHub Pages** workflow (`.github/workflows/mkdocs-gh-pages.yml`) runs on pushes to `main`. It installs MkDocs Material, runs `mkdocs build --strict`, and deploys the `public/` artifact to GitHub Pages.

Enable **Settings → Pages → Build and deployment → GitHub Actions** if the site does not appear after the first successful run.

## Adding pages

1. Add or edit Markdown under `docs/`.
2. Register the page in the `nav` section of `mkdocs.yml`.
3. Run `poetry run mkdocs build --strict` locally before opening a merge request.
