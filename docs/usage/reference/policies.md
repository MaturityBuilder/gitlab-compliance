# policies

Manage compliance policy bundles (catalog, OCI push/pull).

## Usage

```
Usage: gitlab-compliance policies [OPTIONS] COMMAND [ARGS]...
```

## Options

### `--help`

- **Type:** `BOOL`
- **Default:** `false`
- **Usage:** `--help`

Show this message and exit.


## CLI Help

```
Usage: gitlab-compliance policies [OPTIONS] COMMAND [ARGS]...

  Manage compliance policy bundles (catalog, OCI push/pull).

Options:
  --help  Show this message and exit.

Commands:
  doc   Generate a searchable policy catalog from Conftest-style #...
  pull  Pull a compliance policy bundle from an OCI registry.
  push  Push a compliance policy bundle to an OCI registry (Conftest-style).
```
