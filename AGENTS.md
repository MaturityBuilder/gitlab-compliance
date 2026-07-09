# AGENTS.md

## Cursor Cloud specific instructions

### What this is
`gitlab-compliance` (aka `gitlab-docs`) is a **Python 3.12 CLI** managed with **Poetry**. It
generates documentation from `.gitlab-ci.yml` and runs BDD (`behave`/Gherkin) compliance
policies against GitLab CI pipelines. There is no long-running server, database, or frontend —
everything is a CLI invocation over local files, with optional external calls to the GitLab API
(`python-gitlab`) and OCI registries (`oras`).

### Running / testing / linting
Standard commands are in `Makefile`, `pyproject.toml` (`[tool.poetry.scripts]`),
`.pre-commit-config.yaml`, and `.github/workflows/tests.yml`. Common ones:
- Run the CLI: `poetry run gitlab-compliance --help`
- Generate docs: `poetry run gitlab-compliance generate -i <ci.yml> -o <out.md>`
- Compliance check: `poetry run gitlab-compliance check -f <policy-dir> -p <ci.yml>`
- Unit tests: `poetry run pytest tests/ -q`
- BDD tests: `poetry run behave`
- Lint: `poetry run pre-commit run --all-files`

Dependencies are refreshed automatically by the Cursor update script (`poetry install --with dev,docs`),
so you do not need to install them manually.

### Non-obvious caveats
- **`pre-commit run --all-files` fails in this environment.** The `markdownlint-cli2` hook and the
  `default_language_version.node` setting require downloading Node from `nodejs.org`, which is
  **blocked by egress**. GitHub and PyPI are reachable, so all Python hooks work. Run the Python
  hooks individually instead, e.g.:
  `poetry run pre-commit run black --all-files` (and `isort`, `flake8`, `bandit`,
  `end-of-file-fixer`, `trailing-whitespace`, `check-merge-conflict`,
  `check-added-large-files`, `gitlab-compliance`). All of these pass.
- GitLab API-backed compliance scenarios are **skipped** unless a token/project is provided
  (they only fail with `--strict`). No credentials are needed for core offline doc-gen and
  local-policy checks.
- OCI `policies push/pull` requires an OCI registry; not needed for local development.
- `docker-compose.yml` in the repo root does not define real services (it contains pre-commit
  hook YAML) — ignore it for spinning up dependencies.
