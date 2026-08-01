# Gitlab Compliance

[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/MaturityBuilder/gitlab-compliance/badge)](https://scorecard.dev/viewer/?uri=github.com/MaturityBuilder/gitlab-compliance)

**BDD compliance testing and pipeline documentation for GitLab CI/CD** — by
[MaturityBuilder](https://maturitybuilder.github.io/gitlab-compliance/).

[`gitlab-compliance`](https://pypi.org/project/gitlab-compliance/) is a Python CLI
that helps teams catch misconfigurations in GitLab pipelines **before merge**. It
runs readable **Gherkin** policies against `.gitlab-ci.yml` (and optional GitLab
API settings), using the same behaviour-driven style as
[terraform-compliance](https://terraform-compliance.com/) does for Terraform. It
can also **generate** Markdown or HTML reference documentation from your pipeline
YAML.

**Documentation (install, usage, BDD grammar, examples):**
**[https://maturitybuilder.github.io/gitlab-compliance/](https://maturitybuilder.github.io/gitlab-compliance/)**

Source: [github.com/MaturityBuilder/gitlab-compliance](https://github.com/MaturityBuilder/gitlab-compliance)

## Overview

GitLab CI pipelines are YAML with jobs, includes, variables, and workflow rules.
`gitlab-compliance` focuses on [negative
testing](https://en.wikipedia.org/wiki/Negative_testing) — proving that
configuration **does not** violate your standards — rather than end-to-end job
success.

| Workflow | CLI | Purpose |
| -------- | --- | ------- |
| **Compliance** | `gitlab-compliance check` | Fail CI when Gherkin policies are violated |
| **Lock inventory** | `gitlab-compliance lock` | Commit a `.gitlab-ci.lock` inventory and skip jobs when nothing changed |
| **Documentation** | `gitlab-compliance generate` | Build pipeline reference docs from `.gitlab-ci.yml` |

Typical uses:

- Enforce security rules (images, secrets, protected branches, include pins)
- Share policies between developers and security in plain language
- Run offline on YAML; optionally use the GitLab API for project settings and CI variables
- Store policy packs in a separate repo or OCI registry
- Integrate in GitLab CI, GitHub Actions, or local pre-commit hooks

Example policy idea: no job may use a floating `:latest` image tag. See the
[documentation](https://maturitybuilder.github.io/gitlab-compliance/examples/)
for Gherkin examples and step reference.

## Quick start

```bash
# Homebrew
brew tap MaturityBuilder/gitlab-compliance
brew install gitlab-compliance

# Or pip
pip install gitlab-compliance

# Compliance: fail when policies are violated
gitlab-compliance check -f policies/ -p .gitlab-ci.yml

# Documentation: generate a pipeline reference
gitlab-compliance generate -i .gitlab-ci.yml --format swagger-markdown -o pipeline-reference.md
```

Next steps: [Installation](https://maturitybuilder.github.io/gitlab-compliance/installation/) ·
[Usage](https://maturitybuilder.github.io/gitlab-compliance/usage/) ·
[BDD reference](https://maturitybuilder.github.io/gitlab-compliance/bdd-reference/)

## Requirements

- **Python** 3.12+
- **Pipeline file** — `.gitlab-ci.yml` (or path via `-p` / `--input-config`)
- **API checks (optional)** — GitLab token and `--project` or `--group` for settings and variable policies

## Repository

| Resource | Link |
| -------- | ---- |
| **Published docs (GitHub Pages)** | [maturitybuilder.github.io/gitlab-compliance](https://maturitybuilder.github.io/gitlab-compliance/) |
| Contributing | [docs/contributing.md](docs/contributing.md) |
| Security | [SECURITY.md](SECURITY.md) |
| Changelog | [CHANGELOG.md](CHANGELOG.md) |
| This repo’s CI reference | [GITLAB-DOCS.md](GITLAB-DOCS.md) (generated from `.gitlab-ci.yml`) |

Layout: `src/` (CLI and engine), `docs/` (site source), `examples/` (sample policies and fixtures).

## Development

```bash
git clone https://github.com/MaturityBuilder/gitlab-compliance.git
cd gitlab-compliance
poetry install --with dev,docs
poetry run pytest
poetry run pre-commit run --all-files
```

## License

MIT — see [LICENSE](LICENSE). Copyright DevOps Contracting Limited (trading as
Maturity Builder).
