# Using in CI/CD

Run `gitlab-compliance` in your pipeline so policy violations fail before merge.

- **[GitLab CI/CD](gitlab-ci.md):**
  - Project-level jobs, shared templates, reports, rollout
- **[GitLab Functions](gitlab-functions.md):**
  - Experimental `run:` / `func:` example for check + generate docs
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

You can also generate pipeline documentation in CI with
[`generate`](../usage/reference/generate.md) and attach the output as a workflow
artifact (recommended on GitHub so pipeline details stay private):

```bash
gitlab-compliance generate -i .gitlab-ci.yml --format html -o pipeline-reference/index.html
```

Example policies: [Examples](../examples/index.md). Sample generated docs:
[GitLab Docs output example](../examples/gitlab-docs-output-example.md).
