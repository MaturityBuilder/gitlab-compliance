# WHEN Directives

`When` **filters** the stash from the previous step. Entities that do not match are removed.

If the filtered stash is empty, the scenario is **skipped** — this is intentional for optional checks (for example, only jobs that define an `image`).

## Reference

### `When it has {property_name}`

Keep entities that define the property (any value).

```gherkin
When it has image
When it has rules
```

### `When it does not have {property_name}`

Keep entities missing the property.

```gherkin
When it does not have rules
```

### `When its {property_name} is {expected}`

Keep entities where the property equals `expected` (string comparison after normalization).

```gherkin
When its stage is deploy
When its value is false
```

### `When its {property_name} matches "{pattern}"`

Keep entities where the property matches the regular expression.

```gherkin
When its key matches "^(AWS_|DATABASE_)"
When its image matches ":latest$"
```

### `When its name does not start with "{prefix}"`

Keep entities whose name does not start with `prefix` (useful to exclude hidden template jobs).

```gherkin
When its name does not start with "."
```

## Skip behavior

```gherkin
Given I have any job defined
When its stage is nonexistent_stage_xyz
Then it must contain image
```

If no job uses that stage, the scenario skips — it does not fail. This matches terraform-compliance `When` semantics.

### `When a newer release is available`

Keep includes where the GitLab API reports a newer semver tag than the pinned ref.

```gherkin
When a newer release is available
```

### `When a newer release is available for more than {days} days`

**API:** keep includes where a newer semver exists and the latest tag was committed more than `{days}` days ago (adoption grace window exceeded).

```gherkin
When a newer release is available for more than 30 days
```

### `When its release lag exceeds {days} days`

**API:** keep includes where a newer semver exists and the pinned tag is more than `{days}` days older than the latest tag (by commit dates).

```gherkin
When its release lag exceeds 90 days
```

### `When it is not within the latest {count} tags`

**API:** keep includes where the pinned semver ranks below the top `{count}` tags (rank 1 = latest).

```gherkin
When it is not within the latest 5 tags
```

### `When a newer image release is available`

Keep container images where the registry reports a newer tag than the pinned ref.

### `When it is not within the latest {count} image tags`

Filter container images ranked below the top `{count}` registry tags.

Next: [THEN Directives](then.md).
