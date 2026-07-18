# Using in CI/CD

Run `gitlab-compliance` in your pipeline so policy violations fail before merge.

- **[GitLab CI/CD](gitlab-ci.md):**
  - Project-level jobs, shared templates, reports, rollout
- **[GitHub Actions](github-actions.md):**
  - Workflows, Docker publish, pip vs container examples
- **[Pipeline Execution Policy](pipeline-execution-policy.md):**
  - Org-wide injection via GitLab security policies

Typical compliance workflow:

1. Copy or reference policies from
[`examples/example-policies/security/`](https://github.com/MaturityBuilder/gitlab-compliance/tree/main/examples/example-policies/security)
2. Add a compliance job (or inject one via Pipeline Execution Policy)
3. Run `gitlab-compliance check -f policies/security/ -p .gitlab-ci.yml`
4. Optionally pass `--project` for API checks and `--format codequality` for
GitLab reports
5. Fail the job on non-zero exit code

You can also publish pipeline documentation in CI with
[`generate`](../usage/reference/generate.md):

```bash
gitlab-compliance generate -i .gitlab-ci.yml --format html -o public/index.html
```

Example policies: [Examples](../examples/index.md). Sample generated docs:
[Pipeline documentation output example](../examples/gitlab-docs-output-example.md).
