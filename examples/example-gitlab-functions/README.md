# GitLab Functions example (check + generate docs)

Experimental [GitLab Functions](https://docs.gitlab.com/ci/functions/) that wrap
`gitlab-compliance check` and `gitlab-compliance generate`. Functions are
defined locally with [`func.yml`](https://docs.gitlab.com/ci/functions/create/)
and invoked from a job `run:` list.

## Layout

```text
example-gitlab-functions/
  .gitlab-ci.yml          # consumer job using run: / func:
  check/                  # policy check function
  generate-docs/          # HTML (or other) documentation function
```

## Use in your project

1. Copy this directory to your project root (so `./check` and `./generate-docs`
   resolve from `CI_PROJECT_DIR`), or keep it nested and change `func:` paths.
2. Copy policies:

   ```bash
   cp -r examples/example-policies/security policies/security
   ```

3. Point `pipeline` / `input` at your real CI file if it is not `.gitlab-ci.yml`.
4. Ensure the runner can execute GitLab Functions (step runner on the
   executor — see [GitLab Functions](https://docs.gitlab.com/ci/functions/)).

Jobs that use `run:` cannot also use `script`, `before_script`, or
`after_script`. Install the package with a `script:` step inside `run:` as shown
in [`.gitlab-ci.yml`](.gitlab-ci.yml).

## Related documentation

- [GitLab Functions CI/CD guide](../../docs/ci-cd/gitlab-functions.md)
- [GitLab CI/CD guide](../../docs/ci-cd/gitlab-ci.md)
- [`generate` reference](../../docs/usage/reference/generate.md)
