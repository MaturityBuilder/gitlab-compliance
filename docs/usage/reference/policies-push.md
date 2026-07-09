# policies push

Push a compliance policy bundle to an OCI registry (Conftest-style).

## Usage

```
Usage: gitlab-compliance policies push [OPTIONS] TARGET
```

## Options

### `-f, --features` (required)

- **Type:** `STRING`
- **Usage:** `-f, --features`

Directory containing compliance policy .feature files to publish.

### `target` (required)

- **Kind:** argument
- **Type:** `STRING`
- **Usage:** `target`

### `--help`

- **Type:** `BOOL`
- **Default:** `false`
- **Usage:** `--help`

Show this message and exit.


## CLI Help

```
Usage: gitlab-compliance policies push [OPTIONS] TARGET

  Push a compliance policy bundle to an OCI registry (Conftest-style).

Options:
  -f, --features TEXT  Directory containing compliance policy .feature files
                       to publish.  [required]
  --help               Show this message and exit.
```
