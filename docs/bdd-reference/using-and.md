# Using AND

`And` continues the **same step type** as the line above it (`Given`, `When`, or
`Then`).

```gherkin
Scenario: Production tokens must be protected and masked
  Given I have any project ci variable defined
  When its key matches "^(AWS_|DATABASE_|API_KEY)"
  Then its protected must be true
  And its masked must be true
```text

This is equivalent to:

```gherkin
  Then its protected must be true
  Then its masked must be true
```text

## Rules

- `And` after `When` is still a filter — all conditions must be satisfiable by
  the same entity through sequential filtering, or use a single `When` with a
  regex.
- `And` after `Then` adds another assertion on the **same stash**; every entity
  must pass **all** `Then` / `And` assertions.
- Do not use `And` to switch from `Given` to a different entity type; use
  another `Given` or a new scenario.

See [Overview of Scenario Flow](overview.md) for stash behavior.
