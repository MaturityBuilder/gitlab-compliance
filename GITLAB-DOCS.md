# gitlab-compliance

BDD compliance testing and pipeline documentation for GitLab CI/CD — by
[MaturityBuilder](https://maturitybuilder.github.io/gitlab-compliance/).

[`gitlab-compliance` on PyPI](https://pypi.org/project/gitlab-compliance/) runs
Gherkin policies against `.gitlab-ci.yml` (and optional GitLab API settings), and
can generate Markdown or HTML reference docs from your pipeline YAML. The model is
inspired by [terraform-compliance](https://terraform-compliance.com/).

## Quick start

```bash
pip install gitlab-compliance

# Compliance: fail CI when policies are violated
gitlab-compliance check -f policies/ -p .gitlab-ci.yml

# Documentation: generate a pipeline reference
gitlab-compliance generate -i .gitlab-ci.yml --format swagger-markdown -o pipeline-reference.md
```

## Documentation

| Resource | Link |
| -------- | ---- |
| Full docs (install, usage, BDD grammar) | [maturitybuilder.github.io/gitlab-compliance](https://maturitybuilder.github.io/gitlab-compliance/) |
| Contributing | [docs/contributing.md](docs/contributing.md) |
| Security | [SECURITY.md](SECURITY.md) |
| Changelog | [CHANGELOG.md](CHANGELOG.md) |

## Development

```bash
git clone https://github.com/MaturityBuilder/gitlab-compliance.git
cd gitlab-compliance
poetry install --with dev,docs
poetry run pytest
poetry run pre-commit run --all-files
```

## Repository layout

- `src/` — CLI and compliance engine
- `docs/` — Zensical/MkDocs site source
- `examples/` — sample policies and `.gitlab-ci.yml` fixtures
- [`GITLAB-DOCS.md`](GITLAB-DOCS.md) — auto-generated reference for **this** repo’s `.gitlab-ci.yml` (see `OUTPUT_FILE` in `.gitlab-ci.yml`)

## License

MIT — see [LICENSE](LICENSE). Copyright DevOps Contracting Limited (trading as
Maturity Builder).
