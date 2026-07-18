# policies pull

Pull a compliance policy bundle from an OCI registry.

## Usage

```text
Usage: gitlab-compliance policies pull [OPTIONS] TARGET
```

## Options

### `TARGET`

- **Name:** `target`
- **Kind:** Argument
- **Required:** yes
- **Default:** `required`
- **Type:** `STRING`
- **Description:** No description provided.

### `--output-dir, -o`

- **Name:** `output_dir`
- **Kind:** Option
- **Required:** no
- **Default:** `policy`
- **Type:** `STRING`
- **Description:** Directory to extract pulled policies into.


## CLI Help

```text
Usage: gitlab-compliance policies pull [OPTIONS] TARGET

  Pull a compliance policy bundle from an OCI registry.

Options:
  -o, --output-dir TEXT  Directory to extract pulled policies into.  [default:
                         policy]
  --help                 Show this message and exit.
```
