# Usage

Regardless of how you [install](../installation/index.md) `gitlab-compliance`,
the tool supports two primary workflows:

### Compliance (`check`)

1. Author Gherkin policies (`.feature` files) in a directory or OCI registry
2. Point the CLI at your pipeline YAML
3. Optionally enable GitLab API checks with a token and project path
4. Fail the job on violations (default exit code `1`)

```bash
gitlab-compliance check -h
```

### Documentation (`generate`)

1. Point the CLI at your pipeline YAML
2. Choose an output format (`markdown`, `swagger-markdown`, or `html`)
3. Optionally exclude sections or job attributes, or group jobs by attribute

```bash
gitlab-compliance generate -h
gitlab-compliance generate -i .gitlab-ci.yml --format swagger-markdown -o pipeline-reference.md
gitlab-compliance generate -i .gitlab-ci.yml --exclude variables,workflow --group-by stage
```

See [Generate pipeline documentation](reference/generate.md) and [Additional Parameters](additional-parameters.md).

## CLI reference

### `-f` / `--features`

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

### `-p` / `--pipeline`

Path to the GitLab CI pipeline YAML (default: `.gitlab-ci.yml`).

```bash
gitlab-compliance check -f policies/ -p .gitlab-ci.yml
```

### `--project` / `--group`

Enable API-backed scenarios against project or group settings. Requires a GitLab
token — see [Environment Variables](environment-variables.md).

```bash
export GITLAB_TOKEN="<token>"
gitlab-compliance check \
  -f policies/ \
  -p .gitlab-ci.yml \
  --project my-group/my-project
```

API scenarios are **skipped** when connection info is missing unless you pass
`--strict`.

### `--format` / `-o`

Report format and output file:

| Format        | Purpose                                                  |
| ------------- | -------------------------------------------------------- |
| `console`     | Rich tables in the terminal (default)                    |
| `markdown`    | Human-readable report file                               |
| `html`        | HTML report                                              |
| `mr-comment`  | GitLab merge request comment body                        |
| `codequality` | GitLab Code Quality JSON (`gl-code-quality-report.json`) |

```bash
gitlab-compliance check \
  -f policies/ \
  -p .gitlab-ci.yml \
  --format markdown \
  -o COMPLIANCE-REPORT.md
```

### Other commands

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

### Template documentation

For CI template READMEs, use [`document gitstrings`](gitstrings.md) to turn
decorated YAML snippets into tables inside gitstrings markers. Use
[`generate`](reference/generate.md) when you need full pipeline YAML reference
documentation.

## Quick start

**Compliance**

```bash
pip install gitlab-compliance
cp -r examples/example-policies/security/ policies/
gitlab-compliance check -f policies/ -p .gitlab-ci.yml
```

**Documentation**

```bash
pip install gitlab-compliance
gitlab-compliance generate -i .gitlab-ci.yml --format swagger-markdown -o pipeline-reference.md
```

Sample generated output:
[Pipeline documentation output example](../examples/gitlab-docs-output-example.md).

See also [Additional Parameters](additional-parameters.md) and [Environment
Variables](environment-variables.md).
