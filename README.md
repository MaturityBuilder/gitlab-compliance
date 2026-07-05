# Gitlab Docs

## Overview

GitLab Docs is a portable Python CLI for documenting GitLab CI/CD pipelines and enforcing configuration policies. It generates Markdown or HTML documentation from `.gitlab-ci.yml`, and includes a Gherkin-based compliance engine (similar to [terraform-compliance](https://github.com/terraform-compliance/cli) and [Conftest](https://www.conftest.dev/)) for YAML and API-backed checks.

## Key features

| Area | Capability |
|------|------------|
| Documentation | Generate Markdown or Swagger-style HTML from pipeline YAML |
| Auto-update | Refresh docs between markers in README or other files |
| Compliance | Run Gherkin policies against `.gitlab-ci.yml` and GitLab API settings |
| Policy catalog | Index policies with Conftest-style `# METADATA` (ID, title, description) |
| OCI registries | Push and pull versioned policy packs like Conftest |
| Reports | Console (Rich), Markdown, HTML, and GitLab MR comment formats |
| Failure detail | Violations include pipeline file line numbers (`path:line`) |

## Installation

### Python

```bash
pip3 install --user gitlab-docs
```

### Docker

```bash
docker run -v ${PWD}:/gitlab-docs charlieasmith93/gitlab-docs
```

```bash
podman run -it -v $(PWD):/gitlab-docs charlieasmith93/gitlab-docs
```

## Pipeline documentation

Generate documentation from your pipeline file:

```bash
# Markdown (default) into README markers
gitlab-docs generate -i .gitlab-ci.yml -o README.md

# Swagger-style HTML
gitlab-docs generate -i .gitlab-ci.yml --format html -o GITLAB-DOCS.html

# Preview without writing files
gitlab-docs generate -i .gitlab-ci.yml --dry-mode

# Include workflow rules and job rules
gitlab-docs generate -i .gitlab-ci.yml --detailed -o README.md
```

Document specific attributes only:

```bash
gitlab-docs get-attributes -i .gitlab-ci.yml -a stage,image,rules -o JOBS.md
```

## Compliance policies

Run policies from a local directory or OCI registry against your pipeline:

```bash
# YAML-only checks (offline)
gitlab-docs compliance -f policies/ -p .gitlab-ci.yml

# API-backed checks (project settings, CI variables)
gitlab-docs compliance -f policies/ -p .gitlab-ci.yml --project $CI_PROJECT_PATH

# Strict mode: fail when API connection info is missing (default: skip)
gitlab-docs compliance -f policies/ -p .gitlab-ci.yml --strict

# Reports
gitlab-docs compliance -f policies/ -p .gitlab-ci.yml --format markdown -o COMPLIANCE-REPORT.md
gitlab-docs compliance -f policies/ -p .gitlab-ci.yml --format html -o COMPLIANCE-REPORT.html
gitlab-docs compliance -f policies/ -p .gitlab-ci.yml --format mr-comment -o COMPLIANCE-MR-COMMENT.md
```

### Policy metadata (Conftest-style)

Annotate `.feature` files with `# METADATA` blocks for IDs, titles, and descriptions:

```gherkin
# METADATA
# title: Disallow latest image tags
# description: Prevents jobs from using mutable latest tags.
# custom:
#   id: GLCI-IMAGE-PINNING-001
#   severity: HIGH
  Scenario: Job images must not use the latest tag
    Given I have any job defined
    When it has image
    Then its image must not match ":latest$"
```

Generate a searchable policy catalog:

```bash
gitlab-docs compliance-doc -f policies/ -o COMPLIANCE-POLICIES.md
```

### OCI policy registries

Publish and consume policy packs from any OCI-compliant registry (GitLab CR, GHCR, ACR, ECR, etc.):

```bash
docker login registry.example.com

gitlab-docs compliance-push -f policies/ registry.example.com/org/gitlab-ci-policies:1.0.0
gitlab-docs compliance-pull oci://registry.example.com/org/gitlab-ci-policies:1.0.0 -o policies/
gitlab-docs compliance -f oci://registry.example.com/org/gitlab-ci-policies:1.0.0 -p .gitlab-ci.yml --update
```

### Example policy packs

See [example-policies/security/](example-policies/security/) and [docs/compliance-security-examples.md](docs/compliance-security-examples.md) for pinning images, components, fragments, services, rules, templates, and API hardening.

## Command reference

Full auto-generated reference: [docs/command-reference.md](docs/command-reference.md).

### `gitlab-docs`

Top-level CLI group.

```bash
gitlab-docs --help
```

| Command | Description |
|---------|-------------|
| `generate` | Build Markdown or HTML documentation from pipeline YAML |
| `get-attributes` | Document selected YAML attributes as a table |
| `compliance` | Run Gherkin compliance policies |
| `compliance-doc` | Generate policy catalog from `# METADATA` annotations |
| `compliance-push` | Push policy bundle to an OCI registry |
| `compliance-pull` | Pull policy bundle from an OCI registry |
| `release-notes` | Generate release notes from GitLab project commits |
| `generate-html` | Deprecated — use `generate --format html` |

### `generate`

```bash
gitlab-docs generate [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `-i, --input-config` | Pipeline YAML file (default: `.gitlab-ci.yml`) |
| `-o, --output-file` | Output file path |
| `-f, --format` | `markdown` or `html` (default: `markdown`) |
| `--detailed` | Include workflow and job rules |
| `-d, --dry-mode` | Preview without writing files |

### `get-attributes`

```bash
gitlab-docs get-attributes [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `-i, --input-config` | Pipeline YAML file |
| `-o, --output-file` | Output file path |
| `-a, --attributes` | Comma-separated attribute list |
| `-j, --json` | Return JSON instead of Markdown |

### `compliance`

```bash
gitlab-docs compliance [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `-f, --features` | Policy directory or `oci://registry/repo:tag` (**required**) |
| `-p, --pipeline` | Pipeline YAML file (default: `.gitlab-ci.yml`) |
| `--format` | `console`, `markdown`, `html`, `mr-comment` (default: `console`) |
| `-o, --output-file` | Write report to file (non-console formats) |
| `--include-nested / --no-include-nested` | Resolve nested local includes (default: on) |
| `--token` | GitLab API token (or `GITLAB_TOKEN` / `CI_JOB_TOKEN`) |
| `--project` | Project path or ID for API checks (or `CI_PROJECT_PATH`) |
| `--group` | Group path or ID for API checks |
| `--strict` | Fail API scenarios when connection info is missing |
| `--update` | Re-pull policies from OCI before running |
| `--policy-cache-dir` | Cache directory for OCI pulls |
| `--dry-run` | List scenarios without asserting |

### `compliance-doc`

```bash
gitlab-docs compliance-doc [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `-f, --features` | Policy directory or OCI reference (**required**) |
| `--format` | `markdown` or `html` (default: `markdown`) |
| `-o, --output-file` | Output file path |

### `compliance-push`

```bash
gitlab-docs compliance-push -f <policies-dir> <registry/repo:tag>
```

| Argument / option | Description |
|-------------------|-------------|
| `TARGET` | OCI registry reference (e.g. `registry.example.com/org/policies:1.0.0`) |
| `-f, --features` | Local policies directory to publish (**required**) |

### `compliance-pull`

```bash
gitlab-docs compliance-pull <registry/repo:tag> [-o <dir>]
```

| Argument / option | Description |
|-------------------|-------------|
| `TARGET` | OCI registry reference |
| `-o, --output-dir` | Extract destination (default: `policy/`) |

### `release-notes`

Generate release notes from commits since the latest tag (or a chosen baseline tag). Commits are classified using conventional-commit prefixes (`feat`, `fix`, `chore`, and others bucketed as Other). Markdown output groups commits by type and links to GitLab when URLs are available.

```bash
gitlab-docs release-notes \
  --token <token> \
  --projects <id-or-path> \
  [--since-tag v1.0.0] \
  [--markdown <dir>] \
  [--no-write]
```

| Argument / option | Description |
|-------------------|-------------|
| `--token` | GitLab personal access token (`GITLAB_TOKEN`) |
| `--url` | GitLab instance URL (default: `https://gitlab.com`) |
| `--projects` | Project ID or path (repeatable) |
| `--since-tag` | Baseline tag name (default: latest semver tag, else most recent by date) |
| `--markdown` | Output directory for Markdown files (default: `.`) |
| `--no-write` | Console preview only; skip Markdown files |

Example Markdown file: `release_notes_group_project_since_v1.0.0.md`

## Further reading

- [Command reference](docs/command-reference.md) — full Click-generated option details
- [Compliance security examples](docs/compliance-security-examples.md) — policy patterns and CI integration
- [Output example](docs/output-example.md) — sample generated documentation

[comment]: <> (gitlab-docs-opening-auto-generated)

# GITLAB DOCS - .gitlab-ci.yml

## Inputs

|    Key    |        Value        | Description | Options  | Expand |
| :-------: | :-----------------: | :---------: | :------: | :----: |
| job-stage | {'default': 'test'} |   &#x274c;  | &#x274c; |  true  |


## Variables

|     Key     |     Value      | Description | Options  | Expand |
| :---------: | :------------: | :---------: | :------: | :----: |
| APPLICATION |  gitlab-docs   |   &#x274c;  | &#x274c; |  true  |
| OUTPUT_FILE | GITLAB-DOCS.md |   &#x274c;  | &#x274c; |  true  |

## Jobs
<h4><span class="badge text-bg-secondary">.TEST:RULES</span></h4>

<hr>

| **Attribute** | **Value** |
| :-----------: | :-------: |
|   **stage**   |    test   |

| Rule # |                      if                      |  when |
| :----: | :------------------------------------------: | :---: |
|   1    |                $CI_COMMIT_TAG                | never |
|   2    | $CI_PIPELINE_SOURCE == "merge_request_event" |       |
|   3    |   $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH    |       |

<h4><span class="badge text-bg-info">MEGALINTER</span></h4>

<hr>

|   **Attribute**   |           **Value**            |
| :---------------: | :----------------------------: |
| **allow_failure** |              True              |
|    **extends**    |         1. .test:rules         |
|     **image**     | oxsecurity/megalinter-ci_light |

| <span class="badge text-bg-danger">Attribute</span> | <span class="badge text-bg-warning">Key</span> | <span class="badge text-bg-success">Value</span> |
| :-------------------------------------------------: | :--------------------------------------------: | :----------------------------------------------: |
|                      variables                      |               DEFAULT_WORKSPACE                |                 $CI_PROJECT_DIR                  |


<h4><span class="badge text-bg-info">BEHAVE-TESTS</span></h4>

<hr>

| **Attribute** |   **Value**    |
| :-----------: | :------------: |
|  **extends**  | 1. .test:rules |

| <span class="badge text-bg-danger">Attribute</span> | <span class="badge text-bg-warning">Key</span> | <span class="badge text-bg-success">Value</span> |
| :-------------------------------------------------: | :--------------------------------------------: | :----------------------------------------------: |
|                      variables                      |           POETRY_VIRTUALENVS_CREATE            |                      false                       |


<h4><span class="badge text-bg-info">BUMP-VERSION</span></h4>

<hr>

| **Attribute** |   **Value**    |
| :-----------: | :------------: |
|   **image**   | python:3.12.11 |
|   **stage**   |    publish     |

| Rule # |              if             |
| :----: | :-------------------------: |
|   1    | $CI_COMMIT_BRANCH == "main" |

<h4><span class="badge text-bg-secondary">.BUILD:PYTHON</span></h4>

<hr>

|  **Attribute**  | **Value** |
| :-------------: | :-------: |
| **environment** |  release  |
|    **stage**    |   build   |

<h4><span class="badge text-bg-info">TEST-BUILD</span></h4>

<hr>

| **Attribute** |    **Value**     |
| :-----------: | :--------------: |
|  **extends**  | 1. .build:python |
|               |  2. .test:rules  |

<h4><span class="badge text-bg-info">PUBLISH</span></h4>

<hr>

|  **Attribute**  | **Value** |
| :-------------: | :-------: |
|    **cache**    |     []    |
| **environment** |  release  |
|    **stage**    |  publish  |

| Rule # |       if       |
| :----: | :------------: |
|   1    | $CI_COMMIT_TAG |

<h4><span class="badge text-bg-info">DOCKER-BUILD</span></h4>

<hr>

| **Attribute** |      **Value**       |
| :-----------: | :------------------: |
|   **image**   |    docker:latest     |
|  **services** |    1. docker:dind    |
|   **stage**   |        build         |
|    **tags**   | 1. gitlab-org-docker |

| Rule # |                   if                  |
| :----: | :-----------------------------------: |
|   1    | $CI_COMMIT_REF_NAME != $CI_COMMIT_TAG |

[comment]: <> (gitlab-docs-closing-auto-generated)
