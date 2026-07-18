# policies push

Push a compliance policy bundle to an OCI registry (Conftest-style).

## Usage

```text
Usage: gitlab-compliance policies push [OPTIONS] TARGET
```

## Options

### `--features, -f`

- **Name:** `features_dir`
- **Kind:** Option
- **Required:** yes
- **Default:** `required`
- **Type:** `STRING`
- **Description:** Directory containing compliance policy .feature files to publish.

### `TARGET`

- **Name:** `target`
- **Kind:** Argument
- **Required:** yes
- **Default:** `required`
- **Type:** `STRING`
- **Description:** No description provided.


## CLI Help

```text
Usage: gitlab-compliance policies push [OPTIONS] TARGET

  Push a compliance policy bundle to an OCI registry (Conftest-style).

Options:
  -f, --features TEXT  Directory containing compliance policy .feature files
                       to publish.  [required]
  --help               Show this message and exit.
```
