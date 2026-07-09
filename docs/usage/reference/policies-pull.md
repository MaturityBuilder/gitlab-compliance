# policies pull

Pull a compliance policy bundle from an OCI registry.

## Usage

```
Usage: gitlab-compliance policies pull [OPTIONS] TARGET
```

## Options

### `target` (required)

- **Kind:** argument
- **Type:** `STRING`
- **Usage:** `target`

### `-o, --output-dir`

- **Type:** `STRING`
- **Default:** `policy`
- **Usage:** `-o, --output-dir`

Directory to extract pulled policies into.

### `--help`

- **Type:** `BOOL`
- **Default:** `false`
- **Usage:** `--help`

Show this message and exit.


## CLI Help

```
Usage: gitlab-compliance policies pull [OPTIONS] TARGET

  Pull a compliance policy bundle from an OCI registry.

Options:
  -o, --output-dir TEXT  Directory to extract pulled policies into.  [default:
                         policy]
  --help                 Show this message and exit.
```
