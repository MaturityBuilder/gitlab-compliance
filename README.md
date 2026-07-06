# Gitlab Docs

## Contributing

Branch names, commit messages, and PR titles follow [Conventional Commits](https://www.conventionalcommits.org/). Every pull request must link a **user story** GitHub issue (`Closes #123`). See [CONTRIBUTING.md](CONTRIBUTING.md), [AGENTS.md](AGENTS.md), and the [user story issue template](.github/ISSUE_TEMPLATE/user_story.yml).

**Pull requests should target `main`.**

## 📖 Overview

GitLab Docs is your portable, Python-powered sidekick for keeping GitLab CI/CD pipelines well-documented.
If your system supports Python 3, you can install it instantly — no complex setup, no platform restrictions.

### 💡 Why it matters

Code documentation is crucial. Pipeline documentation is critical. As pipelines grow, the what, when, and where of your workflows often get lost. GitLab Docs automatically generates and updates documentation for your pipelines, right alongside your code.

### ✨ Key Features

- Portable — works anywhere Python 3.12 runs
- Markdown, HTML, JSON, and CSV output (see `generate` and pipeline APIs)
- Auto-update mode — refresh documentation between customizable markers
- Multi-command CLI — `generate`, `get-attributes`, `dumps`, `release-notes`

### Python

```bash
pip3 install --user gitlab-docs
```

### Docker / Podman

```bash
docker run -v ${PWD}:/gitlab-docs charlieasmith93/gitlab-docs
```

```bash
podman run -it -v $(PWD):/gitlab-docs charlieasmith93/gitlab-docs
```

### GitHub Actions

CI, PR policy, PyPI trusted publishing, and container builds run via GitHub Actions. See [.github/workflows/README.md](.github/workflows/README.md).

### Documentation

- [docs/index.md](docs/index.md) — overview and generated example
- [docs/command-reference.md](docs/command-reference.md) — CLI reference
- [docs/output-example.md](docs/output-example.md) — sample output

### Quick start

```bash
poetry install
poetry run gitlab-docs generate --help
poetry run gitlab-docs generate -i .gitlab-ci.yml -o README.md --detailed
pytest -q
```
