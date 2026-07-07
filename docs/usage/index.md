# Usage

Regardless of how you [install](../installation/index.md) `gitlab-compliance`, the primary workflow is:

1. Author Gherkin policies (`.feature` files) in a directory or OCI registry
2. Point the CLI at your pipeline YAML
3. Optionally enable GitLab API checks with a token and project path
4. Fail the job on violations (default exit code `1`)

```bash
gitlab-compliance compliance -h
```

## CLI reference

### `-f` / `--features`

**Required** for `compliance`, `compliance-doc`, and `compliance-push`.

Directory of `.feature` policy files, or an OCI reference:

```bash
gitlab-compliance compliance -f policies/ -p .gitlab-ci.yml
gitlab-compliance compliance -f oci://registry.example.com/org/policies:1.0.0 -p .gitlab-ci.yml
```

Use `--update` with OCI references to pull the latest bundle before running.

### `-p` / `--pipeline`

Path to the GitLab CI pipeline YAML (default: `.gitlab-ci.yml`).

```bash
gitlab-compliance compliance -f policies/ -p .gitlab-ci.yml
```

### `--project` / `--group`

Enable API-backed scenarios against project or group settings. Requires a GitLab token — see [Environment Variables](environment-variables.md).

```bash
export GITLAB_TOKEN="<token>"
gitlab-compliance compliance -f policies/ -p .gitlab-ci.yml --project my-group/my-project
```

API scenarios are **skipped** when connection info is missing unless you pass `--strict`.

### `--format` / `-o`

Report format and output file:

| Format | Purpose |
|--------|---------|
| `console` | Rich tables in the terminal (default) |
| `markdown` | Human-readable report file |
| `html` | HTML report |
| `mr-comment` | GitLab merge request comment body |
| `codequality` | GitLab Code Quality JSON (`gl-code-quality-report.json`) |

```bash
gitlab-compliance compliance -f policies/ -p .gitlab-ci.yml --format markdown -o COMPLIANCE-REPORT.md
```

### Other commands

| Command | Description |
|---------|-------------|
| `generate` | Build Markdown or HTML documentation from pipeline YAML |
| `get-attributes` | Export selected job attributes as a table |
| `compliance-doc` | Generate a policy catalog from `# METADATA` annotations |
| `compliance-push` | Publish a policy bundle to an OCI registry |
| `compliance-pull` | Pull a policy bundle from an OCI registry |
| `release-notes` | Generate release notes from GitLab commits |

Auto-generated option details: [Command Reference](reference/command-reference.md) (one page per subcommand).

## Quick start

```bash
pip install gitlab-compliance
cp -r examples/example-policies/security/ policies/
gitlab-compliance compliance -f policies/ -p .gitlab-ci.yml
```

See also [Additional Parameters](additional-parameters.md) and [Environment Variables](environment-variables.md).
