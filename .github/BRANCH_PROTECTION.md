# Branch protection (maintainers)

Enable these settings on **`main`** in GitHub:
**Settings → Branches → Branch protection rules → Add rule** (or edit existing).

Recommended rule for `main`:

1. **Require a pull request before merging** — at least 1 approval (optional for solo maintainers).
2. **Require status checks to pass** — require the **Tests** workflow (`tests.yml`) `test` job (runs pre-commit and coverage).
3. **Require branches to be up to date before merging** — reduces drift.
4. **Do not allow bypassing the above settings** — except for designated admins if needed.
5. **Restrict who can push** — optional; use for org-owned repos.

Also enable **Settings → Code security**:

- **Secret scanning** and **push protection** (GitHub Advanced Security on private repos; public repos get secret scanning where available).

Repository admins must apply these in the GitHub UI; they cannot be fully enforced from this repo without GitHub Apps or organization policy.
