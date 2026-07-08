# Overview of Scenario Flow

## Basics

- **Pipeline YAML** (`.gitlab-ci.yml` and resolved local includes) defines jobs,
  variables, workflow rules, and `include` entries.
- **`gitlab-compliance`** parses that YAML (and optional GitLab API responses)
  into **entities** — dictionaries with `name`, `properties`, and source line
  numbers.
- **Policies** are `.feature` files. Each scenario walks entities through a
  **stash**: a list narrowed by `Given` and `When`, then checked by `Then`.

Violations report the pipeline file and line number (`path:line`) when
available.

## Given and context

Each step operates on the current **stash**.

- `Given` sets the initial stash (all jobs, all includes of a type, a named
  project setting, etc.).
- `When` **filters** the stash. If no entities match, the scenario is
  **skipped** (not failed).
- `Then` **asserts** on every entity in the stash. If any entity fails, the
  scenario **fails**.

Typical structure:

```gherkin
Scenario: Job images must not use latest
  Given I have any job defined
  When it has image
  Then its image must not match ":latest$"
```

`Given`, `When`, and `Then` can be interleaved, but most policies use the order
above.

### Multiple Given steps

A second `Given` **replaces** the stash (like terraform-compliance). Use this
when you need a different entity type mid-scenario:

```gherkin
Given I have any job defined
Given I have include type "component" defined
Then its version must match "^\d+\.\d+\.\d+"
```

For preconditions, prefer a `Background` block or separate scenarios.

## When filters

`When` removes entities that do not match. The stash passed to the next step is
only the matching subset.

```gherkin
Given I have any job defined
When its stage is deploy
Then it must contain rules
```

Only jobs in stage `deploy` are asserted. Jobs in other stages are ignored. If
no job is in `deploy`, the scenario is skipped.

## Then assertions

`Then` requires **all** entities in the stash to satisfy the condition. One
failure fails the scenario.

```gherkin
Given I have any job defined
Then it must contain rules
```

Every job must define `rules:`.

## API-backed scenarios

Steps like `Given I have project setting "public_jobs" defined` call the GitLab
API. Without a token and `--project`, these scenarios are **skipped** by
default. Use `--strict` to fail instead.

See [Environment Variables](../usage/environment-variables.md).

## Policy metadata

Annotate features and scenarios with `# METADATA` for IDs, titles, and severity
— see [Policy Metadata](metadata.md).

For matrix policies with **Scenario Outline** and **Examples** tables, see
[Advanced scenarios](advanced-scenarios.md).
