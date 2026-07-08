# Scenario Outline deep-dive

This page supplements [Advanced scenarios](advanced-scenarios.md) with Behave
expansion and reporting details.

## How Behave expands outlines

At parse time, a `Scenario Outline` plus `Examples` is a single template. At run
time, Behave builds one scenario per Examples row and substitutes placeholders
into each step.

A two-row outline therefore produces two executed scenarios, named like:

```text
Variables must match pattern -- @1.1
Variables must match pattern -- @1.2
```

`gitlab-compliance` collects results from these expanded rows individually and
maps metadata using the normalized outline title (`Variables must match pattern`).

## Placeholder rules

| Examples header | Step placeholder |
| ----------------- | ------------------ |
| `name` | `<name>` |
| `pattern` | `"<pattern>"` inside quoted `must match` steps |
| `conditional key` | `<conditional key>` |
| `input` | `<input>` in `When the entity input <input> equals <value>` |

**Do not** quote placeholders used with `When its {property} is {value}` — the
matcher treats quoted text as part of the literal value (`"RUNNER"` ≠ `RUNNER`).

## Reporting

When an expanded scenario name differs from the outline title, failure messages
may include the normalized outline name in brackets for clarity.

Console and markdown reports list each expanded row with its policy ID and
status. Skipped rows (no entities matched the `When` filter) appear as
`SKIPPED`, not failed.

## `# METADATA` on outlines

```gherkin
# METADATA
# title: Variables must match pattern
# custom:
#   id: GLCI-VARIABLES-001
#   severity: MEDIUM
  Scenario Outline: Variables must match pattern
    ...
```

All expanded rows share the same policy ID and title from the outline metadata
block.

## See also

- [Advanced scenarios](advanced-scenarios.md)
- [WHEN Directives](when.md)
- [THEN Directives](then.md)
