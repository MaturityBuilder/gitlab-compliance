# AGENTS.md

## Cursor Cloud specific instructions

`gitlab-compliance` is a single Python CLI (Poetry, Python 3.12) — BDD compliance
testing and documentation generation for GitLab CI YAML. There is no server,
database, or GUI; everything runs from the terminal. The update script runs
`poetry install` on startup, which installs the main, `dev`, and `docs`
dependency groups plus the project itself (editable), so the `gitlab-compliance`
console script is available via `poetry run`.

### Running / testing / linting (standard commands)
- Run the app: `poetry run gitlab-compliance --help` (core commands: `check`,
  `generate`). The legacy `gitlab-docs` script is a deprecated alias.
- Tests: `poetry run pytest` and `poetry run behave` — run both from the repo
  root (see `docs/contributing.md`).
- Lint: `poetry run pre-commit run --all-files` (hooks defined in
  `.pre-commit-config.yaml`: black, isort, flake8, bandit, markdownlint).
- Docs site: `poetry run zensical serve` / `poetry run zensical build --strict`.

### Non-obvious caveats
- Source lives under `src/` and is imported as `src.*` (e.g. `src.compliance`).
  Tests and the CLI rely on running from the repo root so `import src...`
  resolves; there is no top-level package rename.
- `check -f/--features` expects a **directory** of `.feature` files (or an
  `oci://` reference), not a single `.feature` file — passing a file path raises
  `FileNotFoundError`.
- Network egress is required and is NOT open by default on Cursor Cloud:
  `poetry install` and the `pre-commit` hooks download from `pypi.org` and
  `files.pythonhosted.org` (and hook repos from `github.com`). If those domains
  are not allowlisted, dependency install and linting will fail with connection
  resets; add them under the agent's Network Access settings.
