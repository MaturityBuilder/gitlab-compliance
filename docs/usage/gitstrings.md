# Gitstrings (inline YAML)

Gitstrings renders ` ```yaml gitstrings ` fenced blocks in markdown into **marker-delimited** tables, the same way [`generate`](reference/generate.md) refreshes pipeline documentation without touching the rest of your README.

## When to use

| Command | Input | Output region |
|---------|--------|----------------|
| `document gitstrings` | Markdown with inline YAML snippets | `gitlab-compliance-gitstrings-*` markers |
| `generate` | Full `.gitlab-ci.yml` | `gitlab-compliance-opening-*` markers |

Use gitstrings for **ci-template READMEs** and component docs where you keep small YAML fragments next to prose. Use `generate` for a full pipeline reference.

## Quick start

Add gitstrings markers once where generated tables should appear:

```markdown
[comment]: <> (gitlab-compliance-gitstrings-opening-auto-generated)
[comment]: <> (gitlab-compliance-gitstrings-closing-auto-generated)
```

Then run:

```bash
gitlab-compliance document gitstrings -i README.md
gitlab-compliance document gitstrings -i docs/snippets.md -o README.md
gitlab-compliance document gitstrings -i README.md --dry-mode
```

## Authoring fenced blocks

Only fences tagged `yaml gitstrings` are processed. Ordinary ` ```yaml ` blocks are ignored.

````markdown
```yaml gitstrings
# @title Variables
# @render variables
variables:
  APPLICATION: my-app
```
````

## Directives

| Directive | Purpose |
|-----------|---------|
| `# @title <heading>` | `##` heading above this fragment’s tables |
| `# @render <mode>` | `variables`, `inputs`, `jobs`, or `auto` (default) |
| `# @output <path>` / `# @output-file` | Write this fragment to another file’s gitstrings markers (relative to `-i`) |
| `# @description` | Multi-line prose above tables (continuation lines are `#` comments) |

### Multi-line descriptions

**Fragment prose** (above tables):

```yaml
# @description
#   Use these inputs when including this component.
# @render inputs
spec:
  inputs:
    job-stage:
      default: test
```

**Per-field** (GitLab YAML block scalars become `<br>` in table cells):

```yaml
variables:
  DEPLOY_ENV:
    value: production
    description: |
      Target environment.
      Use staging on feature branches only.
```

## Output behavior

- Only the **gitstrings marker block** on each target file is replaced.
- Default output file: `-o` / `--output` / `--output-file`, or `-i` when omitted.
- Per-fence `# @output` overrides the CLI default for that snippet.
- `--keep-source` (default): collapsible `<details>` with source YAML inside the marker block.
- Safe to run on the same README as `generate`; each command updates its own marker pair.

## CI example

```yaml
doc:gitstrings:
  image: python:3.12
  stage: test
  script:
    - pip install gitlab-compliance
    - gitlab-compliance document gitstrings -i README.md
```

See [GitLab CI/CD](../ci-cd/gitlab-ci.md) for broader pipeline integration.

## Troubleshooting

| Issue | What to check |
|-------|----------------|
| No output updated | At least one ` ```yaml gitstrings ` fence in `-i` |
| Invalid YAML | Remove or fix `# @` directives; they are stripped before parsing |
| Tables empty | Set `# @render` explicitly or ensure YAML matches `variables` / `spec.inputs` / job shape |
