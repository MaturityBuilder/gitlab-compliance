# BDD Reference

Policies are [Gherkin](https://cucumber.io/docs/gherkin/) features. Each **Scenario** follows the same flow as [terraform-compliance](https://terraform-compliance.com/pages/bdd-references/overview/):

## Scenario flow

```
Given   → set the entity stash (jobs, includes, settings, …)
When    → filter the stash (skip scenario if nothing matches)
Then    → assert on every entity left in the stash (fail on violation)
And     → continue the previous step type
```

## Topics

| Topic | Page |
|-------|------|
| [Overview of Scenario Flow](overview.md) | Stash, skip vs fail, typical patterns |
| [GIVEN Directives](given.md) | Entity selection |
| [WHEN Directives](when.md) | Filtering |
| [THEN Directives](then.md) | Assertions |
| [Using AND](using-and.md) | Chaining steps |
| [Policy Metadata](metadata.md) | `# METADATA` annotations and catalogs |

## Related

Example policies live under [Examples](../examples/index.md).
