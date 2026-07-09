# AGENTS.md

## Cursor Cloud specific instructions

### What this project is
`gitlab-docs` / `gitlab-compliance` is a single-product **Python 3.12 CLI** managed by
**Poetry** (`pyproject.toml` + `poetry.lock`). It generates docs from `.gitlab-ci.yml`
and runs a Gherkin/BDD compliance engine. There is **no server, database, or
long-running service** — the product is a one-shot CLI that operates on local YAML
files and (optionally) calls the GitLab API and OCI registries.

### Network / egress requirement (important)
Installing dependencies requires outbound access to **PyPI**. In restricted Cloud
environments only `github.com` is reachable by default, and `poetry install` /
`pip install` will fail with `Connection reset by peer`. If dependency install fails,
ask the user to allowlist `pypi.org` and `files.pythonhosted.org` in the agent's
Network Access settings. External compliance flows also need `gitlab.com` (GitLab
API) and any OCI registry host you push/pull to.

### Poetry on PATH gotcha
Poetry is installed via `pip install --user`, so its console script lands in
`~/.local/bin`, which is **not always on PATH** in non-login shells. If `poetry` is
not found, invoke it as `python3 -m poetry ...` (works regardless of PATH) or add
`~/.local/bin` to PATH for the session.

### Run / test / lint / build
Standard commands live in the `Makefile`, `pyproject.toml` (`[tool.poetry.scripts]`),
and `.gitlab-ci.yml` (`behave-tests` job). Key ones:

- Install deps: `python3 -m poetry install`
- Run the CLI: `python3 -m poetry run gitlab-compliance --help`
  - Generate docs: `python3 -m poetry run gitlab-docs generate -i .gitlab-ci.yml --dry-mode`
  - Offline compliance: `python3 -m poetry run gitlab-docs compliance -f example-policies/security/ -p .gitlab-ci.yml`
- Tests (BDD + unit under coverage, gate 70%, matches CI):
  - `python3 -m poetry run coverage erase`
  - `python3 -m poetry run coverage run -m behave`
  - `python3 -m poetry run coverage run -a -m pytest tests/ -v`
  - `python3 -m poetry run coverage report --fail-under 70`
  - (or individually: `python3 -m poetry run behave` and `python3 -m poetry run pytest tests/ -v`)
- Lint: `pre-commit run --all-files` (black, isort, flake8, bandit). `pre-commit` is not a
  project dependency — install it separately (`pip install --user pre-commit`). Note: the
  black/isort/end-of-file-fixer/trailing-whitespace hooks **rewrite files in place**, so this
  command will modify the working tree; `git restore .` to undo. On the current codebase
  black/isort/flake8/bandit already report pre-existing findings (e.g. bandit's configured
  path `gitlab_docs` does not exist — the package dir is `src`). Real CI lint uses MegaLinter
  via `npx mega-linter-runner` (needs npm), and the `.gitlab-ci.yml` test job does not gate on lint.
- Build (wheel/sdist): `python3 -m poetry build`
- Docs site (optional): `python3 -m poetry run mkdocs serve` / `mkdocs build --strict`

### Gotchas
- The `.pre-commit-config.yaml` includes a local `gitlab-docs` hook that runs the CLI
  itself; it needs the package installed to run.
- The root `docker-compose.yml` is a mislabeled placeholder (it contains
  pre-commit-hook YAML), not a real service definition — do not rely on it.
- Offline compliance/tests work without any tokens; API-backed scenarios are skipped
  when no `GITLAB_TOKEN` is set unless `--strict` is passed.
