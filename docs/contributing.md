# Contributing

Thank you for contributing to **gitlab-compliance**.

## Development setup

```bash
git clone https://github.com/MaturityBuilder/gitlab-compliance.git
cd gitlab-compliance
poetry install --with docs
poetry run gitlab-compliance --help
```

## Tests

```bash
poetry run pytest
poetry run behave
```

## Pre-commit

```bash
poetry install
poetry run pre-commit install
poetry run pre-commit run --all-files
```

Hooks are defined in [`.pre-commit-config.yaml`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/.pre-commit-config.yaml). CI runs the same checks via [`.github/workflows/pre-commit.yml`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/.github/workflows/pre-commit.yml).

## Documentation

Docs are built with [MkDocs Material](https://squidfunk.github.io/mkdocs-material/). Structure mirrors [terraform-compliance.com](https://terraform-compliance.com/).

```bash
poetry install --with docs
poetry run mkdocs serve
poetry run mkdocs build --strict
```

When adding pages:

1. Create Markdown under `docs/`
2. Register the page in `nav` inside `mkdocs.yml`
3. Run `mkdocs build --strict` before opening a pull request

## Policy and BDD changes

- Step definitions live under `src/compliance/behave_support/steps/`
- Update [BDD Reference](bdd-reference/index.md) when adding new `Given` / `When` / `Then` sentences
- Add example `.feature` files under `examples/examples/example-policies/` and a matching [Examples](examples/index.md) page

## Pull requests

- Keep changes focused
- Include tests for new compliance steps or CLI behavior
- Update docs for user-facing changes

Report issues on [GitHub](https://github.com/MaturityBuilder/gitlab-compliance/issues).
