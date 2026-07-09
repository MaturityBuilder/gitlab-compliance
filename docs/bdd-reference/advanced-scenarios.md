# Advanced scenarios

This guide covers **Scenario Outline** policies with **Examples** tables — useful
when one policy must cover many variable names, allowed values, or component
input combinations without duplicating scenarios.

For the standard `Scenario:` flow, see [Overview of Scenario Flow](overview.md).

## When to use outlines

Use a plain `Scenario:` when you check one fixed rule (for example, “deploy jobs
must define `rules:`”).

Use a **Scenario Outline** when the same steps apply to a **matrix** of values:

- Pipeline variable keys and allowed values or regex patterns
- Component `inputs` with conditional constraints on other fields
- Any allowlist you would otherwise copy across multiple scenarios

Bundled policies shipped with `--with-builtin` use outlines for variable
allowlists and component input matrices.

## Scenario Outline syntax

```gherkin
Scenario Outline: Pipeline variables must match allowed patterns
  Given I have any variable defined
  When its key is <name>
  Then its value must match "<pattern>"

  Examples:
    | name        | pattern                    |
    | APPLICATION | .+                         |
    | ENVIRONMENT | prod,uat,dev               |
    | ROLE        | ^(backend\|frontend\|ops)$ |
```

Behave expands each Examples row into a separate run (for example
`Pipeline variables must match allowed patterns -- @1.1`). Reports and metadata
lookup use the outline title without the `@1.1` suffix.

Placeholders in steps must match column headers:

- Column `name` → `<name>` in steps
- Column `conditional key` → `<conditional key>` in steps (headers with spaces
  become angle-bracket placeholders)

Use **unquoted** placeholders for `When its {property} is {value}` steps.
Keep quotes on `Then … must match "<pattern>"` when the cell may contain regex
or comma lists.

## Value spec rules (Examples cells)

Every value cell in an Examples table is interpreted by `match_value_spec`:

| Form | Detection | Meaning |
| ------ | ----------- | --------- |
| **Literal** | Single token, no comma | Exact string match |
| **Comma list** | Contains `,` and does not look like regex | Actual must equal **one** listed value (OR / allowlist) |
| **Regex** | Starts with `^`, ends with `$`, contains `\|`, or `/pattern/` wrapper | Full-string regex match |

Examples:

| Cell value | Matches |
| ------------ | --------- |
| `prod` | Only `prod` |
| `prod,uat,dev` | `prod`, `uat`, or `dev` |
| `trunk,main` | `trunk` or `main` |
| `^(build\|test)$` | `build` or `test` (regex; pipes do not trigger comma-list parsing because of `^`) |

The same rules apply to `Then its value must match "<pattern>"` and to
`Then its <field> must match "<spec>"`.

## Conditional component input matrix

For component includes where one input constrains another field, use a
four-column Examples table:

```gherkin
Scenario Outline: Component input mode constrains dependent fields
  Given I have include type "component" defined
  When the entity input <input> equals <value>
  Then its <conditional key> must match "<conditional value>"

  Examples:
    | input | value   | conditional key | conditional value |
    | mode  | execute | workflow        | trunk,main        |
    | mode  | dry-run | workflow        | gitops            |
```

| Step | Behavior |
|------|----------|
| `When the entity input <input> equals <value>` | Keep includes whose `inputs` dict matches the value spec for that key |
| `Then its <conditional key> must match "<conditional value>"` | Assert the conditional field (input or top-level property) via the same value spec rules |

## Policy metadata on outlines

Attach `# METADATA` above a `Scenario Outline:` the same way as a plain
`Scenario:` — the catalog indexes the outline title (without Behave’s `@1.1`
suffix). See [Policy Metadata](metadata.md).

## Related

- [Scenario Outline deep-dive](scenario-outline.md) — expansion, reporting names
- [Advanced scenario examples](../examples/advanced-scenarios.md) — worked matrices
- [Bundled policies](../usage/index.md#with-builtin) — `--with-builtin` on `check`
