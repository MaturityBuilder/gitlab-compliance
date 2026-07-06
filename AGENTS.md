# Instructions for Cursor (Cloud Agents, Bugbot, and local Agent)

Follow [CONTRIBUTING.md](CONTRIBUTING.md) for this repository.

## Before you change code

1. **Issue first** — Ensure work is tracked with a [user story issue](.github/ISSUE_TEMPLATE/user_story.yml). Target branch for PRs is **`main`**.
2. **User story format** — Issues must include:
   - **As a** \<role\>**, I want** \<capability\>**, so that** \<outcome\>.
   - **Acceptance criteria** as a checklist.
3. **Branch** — `type/short-kebab-description` (e.g. `feat/html-output`) or allowed `cursor/…` agent branches.
4. **Commits** — [Conventional Commits](https://www.conventionalcommits.org/) (`type(scope): imperative summary`).

## Pull requests

- **Title** — Single conventional commit line (squash merge title).
- **Body** — Must include `Closes #<issue>` (or `Fixes` / `Resolves`) for the user story issue.
- **Checklist** — Confirm acceptance criteria in the linked issue are met (or update the issue if scope changed).

## Recording changes

- The **issue** is the record of *what* and *why* (user story + acceptance criteria).
- The **PR** is the record of *how* (diff + conventional title).
- Do not merge work that has no linked issue.

## Commands (when useful)

```bash
pytest -q
python scripts/ci_test.py
gitlab-docs
```

See [.github/workflows/README.md](.github/workflows/README.md) for CI and release.
