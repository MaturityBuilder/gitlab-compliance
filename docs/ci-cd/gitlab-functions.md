# GitLab Functions

Use [GitLab Functions](https://docs.gitlab.com/ci/functions/) (experimental) to
run `gitlab-compliance check` and
[`generate`](../usage/reference/generate.md) as reusable job steps with explicit
inputs and outputs.

!!! warning "Experimental"

    GitLab Functions is an experimental feature and may change. See the
    [GitLab Functions docs](https://docs.gitlab.com/ci/functions/) and
    [create a function](https://docs.gitlab.com/ci/functions/create/).

## Why use functions here

- Package check and documentation generation once; call them from any job
  `run:` list
- Pass policies path, pipeline file, and generate format/output as typed inputs
- Keep install, check, and docs as separate named steps with clear data flow

Functions replace the job `script`. You cannot combine `run:` with
`script` / `before_script` / `after_script` on the same job. Use a `script:`
**step** inside `run:` for one-off commands such as `pip install`.

## Example in this repository

[`examples/example-gitlab-functions/`](https://github.com/MaturityBuilder/gitlab-compliance/tree/main/examples/example-gitlab-functions)
contains:

| Path | Role |
|------|------|
| `check/` | Runs `gitlab-compliance check` |
| `generate-docs/` | Runs `gitlab-compliance generate` and returns `output_path` |
| `.gitlab-ci.yml` | Consumer job: install → check → generate HTML |

Each function is a directory with `func.yml` plus a shell script, as described in
[Create a GitLab Function](https://docs.gitlab.com/ci/functions/create/).

### Consumer job

```yaml
compliance_and_docs:
  image: python:3.12
  stage: test
  run:
    - name: install
      script: pip install --quiet gitlab-compliance
    - name: check
      func: ./check
      inputs:
        policies: policies/security
        pipeline: .gitlab-ci.yml
    - name: generate_docs
      func: ./generate-docs
      inputs:
        input: .gitlab-ci.yml
        format: html
        output: public/index.html
  artifacts:
    paths:
      - public/
```

Copy the example directory to your project root (or adjust `func:` paths), copy
policies into `policies/security/`, and ensure your runner supports the step
runner.

### Function inputs

**check**

| Input | Default | Purpose |
|-------|---------|---------|
| `policies` | `policies/security` | `-f` policy path |
| `pipeline` | `.gitlab-ci.yml` | `-p` pipeline file |

**generate-docs**

| Input | Default | Purpose |
|-------|---------|---------|
| `input` | `.gitlab-ci.yml` | `-i` pipeline file |
| `format` | `html` | `--format` |
| `output` | `public/index.html` | `-o` output path |

`generate-docs` writes an `output_path` output for later steps via
`${{ steps.generate_docs.outputs.output_path }}`.

## Compared to shared job templates

Prefer
[`example-ci/compliance-jobs.yml`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/examples/example-ci/compliance-jobs.yml)
(`extends: .compliance:offline`) when you want classic `script:` jobs without
the Functions runtime.

Use this Functions example when you are already adopting `run:` / `func:` or
want to publish function images later via
[`function/oci/build`](https://docs.gitlab.com/ci/functions/create/#build) and
[`function/oci/publish`](https://docs.gitlab.com/ci/functions/create/#release).

## Related guides

- **[GitLab CI/CD](gitlab-ci.md):** Shared templates, reports, rollout
- **[Pipeline Execution Policy](pipeline-execution-policy.md):** Org-wide
  injection

Back to [Using in CI/CD](index.md).
