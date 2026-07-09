# Gitstrings inline YAML example

Generate README tables from decorated YAML snippets without editing the rest of the page. See the [gitstrings user guide](../usage/gitstrings.md).

## Before

````markdown
# My CI template

Include this component from your pipeline.

```yaml gitstrings
# @title CI inputs
# @description
#   Override the stage when including from a deploy pipeline.
# @render inputs
spec:
  inputs:
    job-stage:
      default: test
      description: |
        Stage for the compliance job.

```

<!-- gitlab-compliance-gitstrings-opening-auto-generated -->
<!-- gitlab-compliance-gitstrings-closing-auto-generated -->

## Support

Open an issue in the template repository.
````

## Run locally

```bash
gitlab-compliance document gitstrings -i README.md

```

## After

The intro, gitstrings fence, and Support section stay unchanged. Only the marker region gains tables (and optional `<details>` source when `--keep-source` is on).

Back to [Examples](index.md).
