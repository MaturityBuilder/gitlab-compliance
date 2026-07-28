# Advanced scenario examples

<p class="example-badges">
  <a class="example-badge example-badge--check" href="../usage/reference/check.md">check</a>
</p>

Worked **Scenario Outline** examples for matrix-style policies. For syntax and
value-spec rules, see [Advanced scenarios](../bdd-reference/advanced-scenarios.md).

## Variable allowlist matrix

Require specific pipeline variables and constrain their values without writing
one scenario per key:

```gherkin
Feature: Pipeline variable allowlist

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

- `ENVIRONMENT` with cell `prod,uat,dev` accepts any of those three literals.
- `ROLE` uses regex alternation; the `^` anchor prevents comma-list parsing.

## Conditional component input matrix

When a component `inputs` value constrains another field:

```gherkin
Feature: Component input constraints

  Scenario Outline: Component input mode constrains dependent fields
    Given I have include type "component" defined
    When the entity input <input> equals <value>
    Then its <conditional key> must match "<conditional value>"

    Examples:
      | input | value   | conditional key | conditional value |
      | mode  | execute | workflow        | trunk,main        |
      | mode  | dry-run | workflow        | gitops            |
```

Example pipeline fragment that satisfies both rows:

```yaml
include:
  - component: gitlab.com/org/my-component@1.0.0
    inputs:
      mode: execute
      workflow: trunk
  - component: gitlab.com/org/my-component@1.0.0
    inputs:
      mode: dry-run
      workflow: gitops
```

A row fails when, for example, `mode: execute` is paired with `workflow: gitops`.

## Bundled outline policies

Enable the package baseline pack alongside your own policies:

```bash
gitlab-compliance check -f policies/ -p .gitlab-ci.yml --with-builtin
```

Bundled files under `src/compliance/builtin_policies/` include:

| File | Outline purpose |
| ------ | ----------------- |
| `variable-allowlist.feature` | Variable key / pattern matrix |
| `component-inputs.feature` | Conditional component input matrix |
| `baseline-jobs.feature` | Plain scenarios (image tag, rules) |
| `include-pinning.feature` | Plain scenarios (component semver) |

## Related

- [Advanced scenarios](../bdd-reference/advanced-scenarios.md)
- [Usage: `--with-builtin`](../usage/index.md#with-builtin)
- [Examples index](index.md)
