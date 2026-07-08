# Sample gitstrings source

```yaml gitstrings
# @title CI inputs (sample pipeline)
# @description
#   Mirrors `spec.inputs` from the repository `.gitlab-ci.yml` sample.
# @render inputs
spec:
  inputs:
    job-stage:
      default: test
      description: |
        Default stage for jobs that extend `.test:rules` in this pipeline.
```

```yaml gitstrings
# @title Sample variables
# @render variables
variables:
  RUNNER:
    value: docker
    description: |
      Runner implementation label for sample jobs.
```

[comment]: <> (gitlab-compliance-gitstrings-opening-auto-generated)
[comment]: <> (gitlab-compliance-gitstrings-closing-auto-generated)
