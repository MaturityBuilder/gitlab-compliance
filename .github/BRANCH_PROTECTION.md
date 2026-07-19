# Branch protection (maintainers)

Enable these settings on **`main`** in GitHub:
**Settings → Branches → Branch protection rules → Add rule** (or edit existing).

Recommended rule for `main`:

1. **Require a pull request before merging** — at least 1 approval (optional for solo maintainers).
2. **Require review from Code Owners** — [`.github/CODEOWNERS`](CODEOWNERS) gates Release Please touchpoints and `release.yml`.
3. **Require status checks to pass** — require the **Tests** workflow (`tests.yml`) **`test`** job. That job is an aggregate gate over `pre-commit`, `unit-test`, and `osv-scanner` (do not require path-filtered Docker checks).
4. **Require branches to be up to date before merging** — reduces drift.
5. **Do not allow bypassing the above settings** — except for designated admins if needed.
6. **Restrict who can push** — optional; use for org-owned repos.

For tag-gated publish credentials, configure GitHub **Environments** `pypi` and
`docker` with deployment tags `v*` only (see
[`.github/workflows/release.yml`](workflows/release.yml) and workflow comments).

Also enable **Settings → Code security**:

- **Secret scanning** and **push protection** (GitHub Advanced Security on private repos; public repos get secret scanning where available).

Repository admins must apply these in the GitHub UI; they cannot be fully enforced from this repo without GitHub Apps or organization policy.
