# policies

Manage compliance policy bundles (catalog, OCI push/pull).

## Usage

```text

Usage: gitlab-compliance policies [OPTIONS] COMMAND [ARGS]...
```

## Options

* `help`:
  * Type: BOOL
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.

## Examples

```bash
gitlab-compliance policies doc -f policies/security/ -o policy-catalog.md
gitlab-compliance policies push -f policies/security/ registry.example.com/org/gitlab-ci-policies:1.0.0
gitlab-compliance policies pull registry.example.com/org/gitlab-ci-policies:1.0.0 -o policies/security/
```

## CLI Help

```text

Usage: gitlab-compliance policies [OPTIONS] COMMAND [ARGS]...

  Manage compliance policy bundles (catalog, OCI push/pull).

Options:
  --help  Show this message and exit.

Commands:
  doc   Generate a searchable policy catalog from Conftest-style #...
  pull  Pull a compliance policy bundle from an OCI registry.
  push  Push a compliance policy bundle to an OCI registry (Conftest-style).

```
