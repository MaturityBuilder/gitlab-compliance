# BDD Reference

Policies are [Gherkin](https://cucumber.io/docs/gherkin/) features. Each
**Scenario** follows the same flow as
[terraform-compliance](https://terraform-compliance.com/pages/bdd-references/overview/):

## Scenario flow

```gherkin
Given   → set the entity stash (jobs, includes, settings, …)
When    → filter the stash (skip scenario if nothing matches)
Then    → assert on every entity left in the stash (fail on violation)
And     → continue the previous step type
```

## Topics

- **[Overview of Scenario Flow](overview.md):**
  - Stash, skip vs fail, typical patterns
- **[GIVEN Directives](given.md):** Entity selection
- **[WHEN Directives](when.md):** Filtering
- **[THEN Directives](then.md):** Assertions
- **[Script steps](script-steps.md):** Embedded CI script Given/When/Then
- **[Using AND](using-and.md):** Chaining steps
- **[Policy Metadata](metadata.md):** `# METADATA` annotations and catalogs
- **[Advanced scenarios](advanced-scenarios.md):** Scenario Outline matrices, value specs
- **[Scenario Outline deep-dive](scenario-outline.md):** Expansion and reporting

## Related

Example policies live under [Examples](../examples/index.md).
