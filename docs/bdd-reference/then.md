# THEN Directives

`Then` **asserts** on every entity in the stash. If any entity fails, the
scenario fails and the compliance run exits with a non-zero code.

## Reference

### `Then it must contain {property_name}`

Every entity must define the property.

```gherkin
Then it must contain rules
Then it must contain image
```text

### `Then it must not contain {property_name}`

No entity may define the property.

```gherkin
Then it must not contain allow_failure
```text

### `Then its {property_name} must be {expected}`

Every entity's property must equal `expected`.

```gherkin
Then its value must be false
Then its protected must be true
Then its masked must be true
```text

### `Then its {property_name} must match "{pattern}"`

Every entity's property must match the **value spec** in `pattern`:

- **Literal** — exact match (`prod`)
- **Comma list** — actual must equal one listed value (`prod,uat,dev`)
- **Regex** — full-string match (`^(backend|frontend)$`)

```gherkin
Then its image must match "^[^\\s]+(:[\\w.-]+|@sha256:[a-f0-9]{64})$"
Then its version must match "^\d+\.\d+\.\d+(-[\w.]+)?$"
Then its value must match "prod,uat,dev"
Then its rules must match "if:"
```text

See [Advanced scenarios](advanced-scenarios.md) for Examples table rules.

### `Then its {property_name} must not match "{pattern}"`

Every entity's property must **not** match the pattern.

```gherkin
Then its image must not match ":latest$"
```text

### `Then its {property_name} must not be null`

Property must be present and non-empty after normalization.

```gherkin
Then its image must not be null
```text

### `Then its extends must include "{template}"`

Job `extends` must reference the template job name.

```gherkin
Then its extends must include ".org:security"
```text

### `Then it must use valid semver`

Every include in the stash must use a valid semver ref (offline check).

```gherkin
Then it must use valid semver
```text

### `Then a newer release must not be available`

**API:** pinned semver must not be behind the latest semver tag on the included
project.

```gherkin
Then a newer release must not be available
```text

### `Then a newer release must not be available for more than {days} days`

**API:** fail when a newer semver exists and the latest tag was published more
than `{days}` days ago. Gives teams a grace period to adopt new upstream
releases.

```gherkin
Then a newer release must not be available for more than 30 days
```text

### `Then its release lag must not exceed {days} days`

**API:** fail when a newer semver exists and the pinned tag trails the latest by
more than `{days}` days (by tag commit dates).

```gherkin
Then its release lag must not exceed 90 days
```text

### `Then it must be within the latest {count} tags`

**API:** pinned semver must rank among the top `{count}` semver tags on the
included project (1 = latest).

```gherkin
Then it must be within the latest 3 tags
```text

### `Then it must use sha256 digest`

Container images must use an immutable `@sha256:` digest (default supply-chain
pin).

### `Then a newer image release must not be available`

**API:** pinned image tag must not be behind the latest registry tag.

### `Then it must be within the latest {count} image tags`

**API:** image tag must rank among the top `{count}` semver tags on the
registry.

### `Then it must track the latest release`

**API:** pinned semver must equal the latest semver tag.

```gherkin
Then it must track the latest release
```text

## Failure output

Failed assertions include entity name, property, expected condition, and source
location in the pipeline file when line metadata is available.

Next: [Using AND](using-and.md).
