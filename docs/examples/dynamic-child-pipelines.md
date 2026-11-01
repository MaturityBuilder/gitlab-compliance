# Dynamic child pipelines

GitLab can [trigger a child pipeline from YAML generated at runtime](https://docs.gitlab.com/ci/pipelines/downstream_pipelines/#dynamic-child-pipelines).
`gitlab-compliance` does **not** run the generator script. After the artifact
exists on disk, it loads that YAML into the same entity stash used by `check`,
`shell-check`, `supply-chain`, and `generate`.

## Parent pipeline

```yaml
generate-config:
  stage: build
  script:
    - generate-ci-config > generated-config.yml
  artifacts:
    paths:
      - generated-config.yml

child-pipeline:
  stage: test
  trigger:
    include:
      - artifact: generated-config.yml
        job: generate-config
```

## Run compliance after generation

```yaml
compliance:
  stage: test
  needs:
    - generate-config
  image: python:3.12
  script:
    - pip install gitlab-compliance
    - gitlab-compliance check -f policies/ -p .gitlab-ci.yml
```

When `generated-config.yml` is present next to the parent pipeline file (or in
the working directory), child jobs are merged and tagged with
`dynamic_parent_job` / `generated_artifact`.

When the artifact is missing, the parent still parses successfully and a
coverage gap is reported with reason `generated_at_runtime`.

## CLI options

| Flag | Purpose |
| ---- | ------- |
| `--resolve-generated` / `--no-resolve-generated` | Enable or disable artifact loading (default: on) |
| `--generated-config PATH` | Merge an extra generated file (repeatable) when the path differs from the declared artifact |

## Example policy

```gherkin
Feature: Generated child pipelines must be available for review
  Scenario: Dynamic child configs were resolved
    Given I have any dynamic child pipeline defined
    Then it must contain resolved
    And its resolved must be true
```

Skip this style of policy for repos that do not use dynamic children, or run it
only in the post-generation compliance job above.
