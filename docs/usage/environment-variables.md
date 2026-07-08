# Environment Variables

`gitlab-compliance` reads these environment variables when CLI flags are
omitted.

## Compliance / API checks

| Variable            | Used for                          | CLI override   |
| ------------------- | --------------------------------- | -------------- |
| `GITLAB_TOKEN`      | GitLab API authentication         | `--token`      |
| `CI_JOB_TOKEN`      | Fallback token in GitLab CI jobs  | `--token`      |
| `CI_PROJECT_PATH`   | Default project for API scenarios | `--project`    |
| `CI_SERVER_URL`     | GitLab instance URL               | `--gitlab-url` |
| `GITLAB_GROUP_PATH` | Group-scoped API scenarios        | `--group`      |

A token alone is enough for **include release checks** against projects
referenced in `include:` entries. Project and group settings still require
`--project` or `--group`.

Example in CI (GitLab):

```yaml
compliance:
  script:
    - pip install gitlab-compliance
    - gitlab-compliance check -f policies/ -p .gitlab-ci.yml --project
      $CI_PROJECT_PATH
```

Locally:

```bash
export GITLAB_TOKEN="glpat-..."
export CI_PROJECT_PATH="my-group/my-project"
gitlab-compliance check -f policies/ -p .gitlab-ci.yml
```

!!! note "Token safety"
    Tokens are read from the environment only. Do not pass tokens through Behave
    userdata or commit them to policy files.

## Strict mode

`--strict` is a CLI flag only (not an environment variable). It controls whether
missing API connection info causes failures instead of skipped scenarios.

## GitLab CI built-ins

In GitLab CI jobs, these variables are usually set automatically and work with
`--project $CI_PROJECT_PATH` without extra configuration:

- `CI_JOB_TOKEN`
- `CI_PROJECT_PATH`
- `CI_SERVER_URL`

See [GitLab CI/CD integration](../ci-cd/gitlab-ci.md) for a full job example.
