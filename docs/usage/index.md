# Usage

`gitlab-compliance` has one preferred entry point:

```bash
gitlab-compliance --help
```

The older `gitlab-docs` command still works as a deprecated alias, but new
automation should use `gitlab-compliance`.

## Choose a workflow

| Goal | Start with | Read next |
| ---- | ---------- | --------- |
| Fail builds on pipeline policy violations | `gitlab-compliance check` | [Additional Parameters](additional-parameters.md) |
| Generate pipeline reference docs | `gitlab-compliance generate` | [Generate reference](reference/generate.md) |
| Document reusable template snippets | `gitlab-compliance document gitstrings` | [Gitstrings guide](gitstrings.md) |
| Publish or consume policy packs | `gitlab-compliance policies` | [Policy commands](reference/policies.md) |

## Compliance checks

1. Author Gherkin policies (`.feature` files) in a directory or OCI registry.
2. Point the CLI at your pipeline YAML.
3. Optionally enable GitLab API checks with a token and project or group path.
4. Let violations fail the job with exit code `1`.

```bash
gitlab-compliance check -h
gitlab-compliance check -f policies/security/ -p .gitlab-ci.yml
```

### API-backed checks

API scenarios are skipped when connection details are missing. Use `--strict` in
CI when missing GitLab API access should fail the run.

```bash
export GITLAB_TOKEN="<token>"
gitlab-compliance check \
  -f policies/security/ \
  -p .gitlab-ci.yml \
  --project my-group/my-project \
  --strict
```

### Report formats

| Format | Command pattern | Output |
| ------ | --------------- | ------ |
| Console | `--format console` | Rich terminal report |
| Markdown | `--format markdown -o COMPLIANCE-REPORT.md` | Human-readable artifact |
| HTML | `--format html -o COMPLIANCE-REPORT.html` | Browser-readable artifact |
| Merge request comment | `--format mr-comment -o COMPLIANCE-MR-COMMENT.md` | Comment body for GitLab API calls |
| Code Quality | `--format codequality` | `gl-code-quality-report.json` |

## Pipeline documentation

1. Point the CLI at your pipeline YAML.
2. Choose an output format: `markdown`, `swagger-markdown`, or `html`.
3. Optionally exclude sections or job attributes.
4. Optionally group jobs by an attribute such as `stage`.

```bash
gitlab-compliance generate -h
gitlab-compliance generate -i .gitlab-ci.yml --format swagger-markdown -o pipeline-reference.md
gitlab-compliance generate \
  -i .gitlab-ci.yml \
  --exclude variables,workflow \
  --group-by stage
```

See [Generate pipeline documentation](reference/generate.md) and
[Additional Parameters](additional-parameters.md).

## Common options

### Policy source: `-f` / `--features`

**Required** for `check`, `policies doc`, and `policies push`.

Directory of `.feature` policy files, or an OCI reference:

```bash
gitlab-compliance check -f policies/ -p .gitlab-ci.yml
gitlab-compliance check \
  -f oci://registry.example.com/org/policies:1.0.0 \
  -p .gitlab-ci.yml
```

Use `--update` with OCI references to pull the latest bundle before running.

### `--with-builtin` {#with-builtin}

Also run bundled baseline policies shipped inside the `gitlab-compliance`
package. Your `-f` directory remains **required**; `--with-builtin` **adds** the
bundled pack alongside your policies.

```bash
gitlab-compliance check -f policies/ -p .gitlab-ci.yml --with-builtin
```

Bundled policies include plain scenarios (job images, include pinning) and
**advanced Scenario Outline** matrices (variable allowlists, component input
constraints). See [Advanced scenarios](../bdd-reference/advanced-scenarios.md).

### Pipeline path: `-p` / `--pipeline`

Path to the GitLab CI pipeline YAML (default: `.gitlab-ci.yml`).

```bash
gitlab-compliance check -f policies/ -p .gitlab-ci.yml
```

## Command map

| Command               | Description                                                       |
| --------------------- | ----------------------------------------------------------------- |
| `check`               | Run Gherkin compliance policies against pipeline YAML             |
| `generate`            | Build Markdown or HTML documentation from pipeline YAML           |
| `get-attributes`      | Export selected job attributes as a table                         |
| `policies doc`        | Generate a policy catalog from `# METADATA` annotations         |
| `policies push`       | Publish a policy bundle to an OCI registry                        |
| `policies pull`       | Pull a policy bundle from an OCI registry                         |
| `release-notes`       | Generate release notes from GitLab commits                        |
| `document gitstrings` | Render inline `yaml gitstrings` fences into README marker blocks  |

For every flag and generated help text, see the
[Command Reference](reference/command-reference.md).

## Template documentation

For CI template READMEs, use [`document gitstrings`](gitstrings.md) to turn
decorated YAML snippets into tables inside gitstrings markers. Use
[`generate`](reference/generate.md) for full pipeline YAML.

```bash
gitlab-compliance document gitstrings -i .gitlab-ci.yml -o README.md
gitlab-compliance document gitstrings -i README.md --dry-mode
```

## Quick starts

**Compliance**

```bash
pip install gitlab-compliance
cp -r examples/example-policies/security/ policies/security/
gitlab-compliance check -f policies/security/ -p .gitlab-ci.yml
```

**Documentation**

```bash
pip install gitlab-compliance
gitlab-compliance generate -i .gitlab-ci.yml --format swagger-markdown -o pipeline-reference.md
```

Sample generated output: [GitLab Docs output example](../examples/gitlab-docs-output-example.md).

See also [Additional Parameters](additional-parameters.md) and [Environment
Variables](environment-variables.md).
