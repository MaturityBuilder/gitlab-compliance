# Contributing

Thank you for contributing to **gitlab-docs**. This project uses [Conventional Commits](https://www.conventionalcommits.org/) for branch names, commit messages, and pull request titles, and expects every pull request to reference a GitHub issue.

## Before you open a pull request

1. Open a GitHub **issue** using the [**User story** template](.github/ISSUE_TEMPLATE/user_story.yml) (blank issues are disabled—use the template).

**Open pull requests against `main`.** The PR diff should be `main...your-branch`.
2. Create a branch from the default branch using the naming rules below.
3. Make commits that follow Conventional Commits.
4. Open a PR whose **title** is a conventional commit message and whose **description** links the issue (`Closes #123`).

### User stories

Record *what* and *why* in the issue before coding:

```text
As a <role>, I want <capability>, so that <outcome>.
```

Add **acceptance criteria** as a checklist. The PR should satisfy those items (or update the issue if scope changes).

**Cursor agents:** see [AGENTS.md](AGENTS.md) for the same rules in agent-oriented form.

## Branch names

Use lowercase **type** + `/` + short **kebab-case** description:

```text
feat/add-html-output
fix/yaml-tab-parse-error
docs/contributing-guide
chore/update-dependencies
ci/pr-policy-checks
test/render-formats
refactor/pipeline-module
```

Allowed types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`.

Optional scope in the description is fine (e.g. `feat/cli-detailed-flag`), but do not use spaces or uppercase in the branch name.

Cloud automation branches under `cursor/` are allowed for agent workflows (e.g. `cursor/gitlab-docs-all-phases-e1a6`).

## Commit messages

Each commit should look like:

```text
<type>(<optional scope>): <short description>

[optional body]

[optional footer: Closes #123]
```

Examples:

```text
feat(render): add CSV export via pytablewriter
fix(ci): install pytablewriter html extra for dominate
docs: document conventional commits in CONTRIBUTING
chore(deps): bump pytest to 8.x
```

Rules:

- Use the imperative mood in the subject (`add` not `added`).
- Keep the subject line ≤ 72 characters when possible.
- Breaking changes: add `!` after type/scope or a `BREAKING CHANGE:` footer.

### Local check (recommended)

Install pre-commit hooks (includes commit-message validation):

```bash
pip install pre-commit
pre-commit install
pre-commit install --hook-type commit-msg
```

## Pull requests

### Title

The PR title must be a **single** Conventional Commit line (this is what we use for squash merges). Same format as commit subjects above.

Good: `fix(tests): install dominate for HTML table output`  
Bad: `Fix tests` or `WIP stuff`

### Link an issue (required)

Every PR must reference at least one issue in the description. Prefer a closing keyword so the issue closes when the PR merges:

```markdown
Closes #42
```

Also valid: `Fixes #42`, `Resolves #42`, or a full issue URL:

```text
https://github.com/MaturityBuilder/gitlab-docs/issues/42
```

The [pull request template](.github/pull_request_template.md) includes a **Linked issue** section—fill it in before requesting review.

### CI

The **PR policy** workflow runs on every pull request and checks:

- Branch name (or allowed `cursor/` prefix)
- PR title (Conventional Commits)
- PR body contains an issue reference

## Development

```bash
pip install -e .
pip install pytest
pytest -q
```

See [.github/workflows/README.md](.github/workflows/README.md) for CI and release automation.
