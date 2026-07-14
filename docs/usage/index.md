# Usage

Regardless of how you [install](../installation/index.md) `gitlab-compliance`,
the tool supports compliance checks, generated pipeline documentation, template
snippet documentation, and policy-pack management.

## Compliance checks

1. Author Gherkin policies (`.feature` files) in a directory or OCI registry
2. Point the CLI at your pipeline YAML
3. Optionally enable GitLab API checks with a token and project path
4. Fail the job on violations (default exit code `1`)

```bash
gitlab-compliance check -h
```

### Local policy directory

```bash
gitlab-compliance check -f policies/security/ -p .gitlab-ci.yml
gitlab-compliance check -f policies/security/ -p .gitlab-ci.yml --with-builtin
```

### OCI policy pack

```bash
gitlab-compliance check -f oci://registry.example.com/org/policies:1.0.0 -p .gitlab-ci.yml
gitlab-compliance check -f oci://registry.example.com/org/policies:1.0.0 -p .gitlab-ci.yml --update
```

### GitLab API-backed policies

API scenarios are **skipped** when connection info is missing unless you pass
`--strict`.

```bash
export GITLAB_TOKEN="YOUR_GITLAB_TOKEN"
gitlab-compliance check -f policies/security/ -p .gitlab-ci.yml --project my-group/my-project
```

## Pipeline documentation

1. Point the CLI at your pipeline YAML
2. Choose an output format (`markdown`, `swagger-markdown`, or `html`)
3. Optionally exclude sections or job attributes, or group jobs by attribute

```bash
gitlab-compliance generate -h
gitlab-compliance generate -i .gitlab-ci.yml --format swagger-markdown -o pipeline-reference.md
gitlab-compliance generate -i .gitlab-ci.yml --exclude variables,workflow --group-by stage
```

See [Generate pipeline documentation](reference/generate.md) and [Additional
Parameters](additional-parameters.md).

## Template snippet documentation

Use [`document gitstrings`](reference/document-gitstrings.md) when a README
contains decorated `yaml gitstrings` snippets, or when a CI YAML file contains
`# @title`, `# @render`, and `# @output` decorators.

```bash
gitlab-compliance document gitstrings -i README.md
gitlab-compliance document gitstrings -i .gitlab-ci.yml -o README.md --include-nested
```

See the [Gitstrings guide](gitstrings.md) for marker blocks, supported
directives, and nested include behavior.

## CLI reference

### `-f` / `--features`

**Required** for `check`, `policies doc`, and `policies push`.

Directory of `.feature` policy files, or an OCI reference.

```bash
gitlab-compliance check -f policies/ -p .gitlab-ci.yml
gitlab-compliance check -f oci://registry.example.com/org/policies:1.0.0 -p .gitlab-ci.yml
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
gitlab-compliance check -f policies/ -p .gitlab-ci.yml --format markdown -o COMPLIANCE-REPORT.md
```

### Other commands

| Command               | Description                                                       |
| --------------------- | ----------------------------------------------------------------- |
| `check`               | Run Gherkin compliance policies against pipeline YAML             |
| `generate`            | Build Markdown, Swagger-style Markdown, or HTML docs              |
| `get-attributes`      | Export selected job attributes as a table                         |
| `policies doc`        | Generate a policy catalog from `# METADATA` annotations           |
| `policies push`       | Publish a policy bundle to an OCI registry                        |
| `policies pull`       | Pull a policy bundle from an OCI registry                         |
| `release-notes`       | Generate release notes from GitLab commits                        |
| `document gitstrings` | Render inline `yaml gitstrings` fences into README marker blocks  |

### Template documentation

For CI template READMEs, use [`document gitstrings`](gitstrings.md) to turn
decorated YAML snippets into tables inside gitstrings markers (alongside
[`generate`](reference/generate.md) for full pipeline YAML).

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

Sample generated output: [GitLab Docs output example](../examples/gitlab-docs-output-example.md).

See also [Additional Parameters](additional-parameters.md) and [Environment
Variables](environment-variables.md).
