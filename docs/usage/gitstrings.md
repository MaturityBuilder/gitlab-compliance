# Gitstrings (inline YAML)

Gitstrings turns **decorated YAML** into **marker-delimited** markdown tables (like [`generate`](reference/generate.md)), without overwriting the rest of your README.

## Two input modes

| Source | How decorators are written |
|--------|----------------------------|
| **CI YAML** (`.gitlab-ci.yml`, `*.yml`) | `# @title`, `# @render`, `# @description`, `# @output` comment lines above the YAML fragment |
| **Markdown** | Same directives inside ` ```yaml gitstrings ` fenced blocks |

For CI files, only the annotated fragment is read (for example the `variables:` map stops before the next top-level key such as `image:`).

```bash
# Scan decorators in pipeline YAML; default output README.md in the same directory
gitlab-compliance document gitstrings -i .gitlab-ci.yml

# Explicit output markdown
gitlab-compliance document gitstrings -i .gitlab-ci.yml -o README.md
```

## When to use

| Command | Input | Output region |
|---------|--------|----------------|
| `document gitstrings` | CI YAML decorators and/or markdown fences | `gitlab-compliance-gitstrings-*` markers |
| `generate` | Full `.gitlab-ci.yml` (no decorators required) | `gitlab-compliance-opening-*` markers |

Use gitstrings for **documented fragments** (inputs, variables, small job snippets). Use `generate` for a full pipeline reference.

## Quick start

Add gitstrings markers once where generated tables should appear:

```markdown
<!-- gitlab-compliance-gitstrings-opening-auto-generated -->
<!-- gitlab-compliance-gitstrings-closing-auto-generated -->
```

Annotate `.gitlab-ci.yml` (or use markdown fences), then run:

```bash
gitlab-compliance document gitstrings -i .gitlab-ci.yml
gitlab-compliance document gitstrings -i README.md
gitlab-compliance document gitstrings -i docs/snippets.md -o README.md
gitlab-compliance document gitstrings -i .gitlab-ci.yml --dry-mode
```

## Authoring in `.gitlab-ci.yml`

```yaml
# @title Pipeline inputs
# @description
#   Inputs for component consumers.
# @render inputs
# @output README.md
spec:
  inputs:
    job-stage:
      default: test
      description: Stage for test jobs.
```

## Authoring fenced blocks (markdown)

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
| `# @render <mode>` | `variables`, `inputs`, `jobs`, `includes` (or `include`), `auto`; or a **dot path** (e.g. `megalinter.variables`, `spec.inputs`, `include`) |
| `# @sensitive <path>` | Mask values at a YAML path (repeatable; comma-separated). Rows still appear; value cells show `****` (e.g. `megalinter.variables.mode.value`) |
| `# @output <path>` / `# @output-file` | Write this fragment to another file’s gitstrings markers (relative to `-i`). Ignored when you pass `-o` / `--output` on the CLI. |
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

### Includes fragment

Document the pipeline `include` list as a table (local, project, component, remote, template):

```yaml
# @title Pipeline includes
# @description
#   External and local CI fragments consumed by this configuration.
# @render includes
include:
  - local: gitlab-ci/hidden.jobs.yml
  - project: my-group/my-project
    ref: 1.2.3
    file: ci/workflow.yml
```

Use `@render includes` for legacy fragment mode (the fenced `include` list in the block). Use `@render include` for **path mode** on the top-level `include` key — with `-i` set to a CI YAML file, that resolves the full file’s `include` list (not only the annotated fragment).

#### `--include-nested` scope (on disk only)

| Include type | In the table | With `--include-nested` |
|--------------|--------------|-------------------------|
| **`local:`** | One row per entry | Also walks **files on disk** relative to `-i`, merges `include` entries from those YAML files (and their nested **`local:`** chains). Same behavior as `generate` / `collect_pipeline_data`. |
| **`project:`**, **`component:`**, **`remote:`**, **`template:`** | One row per stanza (project/URL, ref/version, file, variables, rules) | **Not expanded** — no GitLab or registry fetch; upstream trees are out of scope for now. |

Requirements for nesting:

- `-i` must be the **root CI YAML file** (`.yml` / `.yaml`) so `local:` paths resolve on disk.
- Markdown-only scans (fences in README) document only the fenced `include` list; nesting does not apply.

Without `--include-nested`, only `include` entries in the **annotated fragment** are shown (or the full top-level `include` list when using path `include` on a CI file).

```bash
gitlab-compliance document gitstrings -i .gitlab-ci.yml --include-nested -o GITLAB-DOCS.md
```

### Path-based render and sensitive values

Use dot paths on `@render` to control exactly which YAML subtree becomes a table. Parent segments work too (`variables`, `megalinter.variables`). Job names match case-insensitively when resolving paths against a full `.gitlab-ci.yml`.

Use `@sensitive` with a path to the **value leaf** (often ending in `.value` or `.default`) so the row is still documented but the cell is masked.

```yaml
# @title Megalinter mode (masked)
# @render megalinter.variables.mode
# @sensitive megalinter.variables.mode.value
variables:
  APPLICATION: my-app
```

When `-i` is a CI YAML file, paths resolve against the **entire** pipeline file, not only the annotated fragment.

## Output behavior

Generated fragments are rendered as **markdown pipe tables** (variables, inputs, jobs, and path-based slices). Multi-line or list values use `<br>` inside table cells rather than bullet lists.

- Only the **gitstrings marker block** on each target file is replaced.
- Default output file: `-o` / `--output` / `--output-file`, or `-i` when omitted (for CI YAML, `README.md` beside the file).
- When **`-o` is set**, every fragment writes to that file and **`# @output` is ignored**.
- Without **`-o`**, per-fragment `# @output` overrides the default for that snippet only.
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
| Tables empty | Set `# @render` explicitly or ensure YAML matches `variables` / `spec.inputs` / `include` / job shape |
| Nested includes missing | Use `-i` on the root `.gitlab-ci.yml` and `--include-nested`; only **`local:`** files on disk are walked (not project/component trees) |
