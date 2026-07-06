# GitLab Compliance

**GitLab Compliance** (PyPI package [`gitlab-docs`](https://pypi.org/project/gitlab-docs/)) is a portable CLI for documenting GitLab CI/CD pipelines and enforcing configuration policies. It generates Markdown or HTML from `.gitlab-ci.yml`, and includes a Gherkin-based compliance engine (similar to [terraform-compliance](https://github.com/terraform-compliance/cli) and [Conftest](https://www.conftest.dev/)) for YAML and API-backed checks.

Source code: [MaturityBuilder/gitlab-compliance](https://github.com/MaturityBuilder/gitlab-compliance).

## Key features

| Area | Capability |
|------|------------|
| Documentation | Generate Markdown or Swagger-style HTML from pipeline YAML |
| Auto-update | Refresh docs between markers in README or other files |
| Compliance | Run Gherkin policies against `.gitlab-ci.yml` and GitLab API settings |
| Policy catalog | Index policies with Conftest-style `# METADATA` (ID, title, description) |
| OCI registries | Push and pull versioned policy packs like Conftest |
| Reports | Console (Rich), Markdown, HTML, GitLab MR comment, and Code Quality JSON formats |
| Failure detail | Violations include pipeline file line numbers (`path:line`) |

## Installation

### Python (recommended)

Install from PyPI. Two CLI entry points are available; prefer **`gitlab-compliance`** for new usage.

| Command | Status |
|---------|--------|
| `gitlab-compliance` | **Preferred** — compliance-first naming |
| `gitlab-docs` | **Deprecated** — same tool; shows a deprecation notice |

```bash
pip install --user gitlab-docs
gitlab-compliance --help
```

From a clone of this repository (development):

```bash
poetry install
poetry run gitlab-compliance --help
```

### Docker

```bash
docker run -v "${PWD}:/gitlab-docs" charlieasmith93/gitlab-docs
```

```bash
podman run -it -v "$(pwd):/gitlab-docs" charlieasmith93/gitlab-docs
```

Mount your project directory at `/gitlab-docs` so the container can read `.gitlab-ci.yml` and write reports.

## How to use

### 1. Document a pipeline

Generate reference documentation from your pipeline file:

```bash
# Markdown into README markers (default)
gitlab-compliance generate -i .gitlab-ci.yml -o README.md

# Swagger-style HTML
gitlab-compliance generate -i .gitlab-ci.yml --format html -o GITLAB-DOCS.html

# Preview in the terminal without writing files
gitlab-compliance generate -i .gitlab-ci.yml --dry-mode

# Include workflow rules and per-job rules
gitlab-compliance generate -i .gitlab-ci.yml --detailed -o README.md
```

Export selected job attributes only:

```bash
gitlab-compliance get-attributes -i .gitlab-ci.yml -a stage,image,rules -o JOBS.md
```

### 2. Run compliance policies

Policies are Gherkin `.feature` files. Run them against local YAML or combine with the GitLab API for project settings.

```bash
# Offline YAML checks
gitlab-compliance compliance -f policies/ -p .gitlab-ci.yml

# API-backed checks (CI variables, project settings)
export GITLAB_TOKEN="<token>"
gitlab-compliance compliance -f policies/ -p .gitlab-ci.yml --project my-group/my-project

# Fail when API scenarios cannot run (default: skip)
gitlab-compliance compliance -f policies/ -p .gitlab-ci.yml --strict

# Reports for CI and merge requests
gitlab-compliance compliance -f policies/ -p .gitlab-ci.yml --format markdown -o COMPLIANCE-REPORT.md
gitlab-compliance compliance -f policies/ -p .gitlab-ci.yml --format mr-comment -o COMPLIANCE-MR-COMMENT.md
gitlab-compliance compliance -f policies/ -p .gitlab-ci.yml --format codequality -o gl-code-quality-report.json
```

Generate a policy catalog from `# METADATA` annotations:

```bash
gitlab-compliance compliance-doc -f policies/ -o COMPLIANCE-POLICIES.md
```

### 3. Share policies via OCI

```bash
docker login registry.example.com

gitlab-compliance compliance-push -f policies/ registry.example.com/org/gitlab-ci-policies:1.0.0
gitlab-compliance compliance-pull oci://registry.example.com/org/gitlab-ci-policies:1.0.0 -o policies/
gitlab-compliance compliance -f oci://registry.example.com/org/gitlab-ci-policies:1.0.0 -p .gitlab-ci.yml --update
```

### Example policies

Browse the [security example policy pack](https://github.com/MaturityBuilder/gitlab-compliance/tree/main/example-policies/security) in the repository, and see [Compliance security examples](compliance-security-examples.md) for pinning images, components, fragments, services, rules, templates, and API hardening.

## Command reference

Full option lists and subcommands: [Command reference](command-reference.md).

## Further reading

- [Compliance security examples](compliance-security-examples.md) — policy patterns and CI integration
- [Output example](output-example.md) — sample generated pipeline documentation
- [Site build & publish](site-documentation.md) — MkDocs site, review builds, and Pages deployment

[comment]: <> (gitlab-docs-opening-auto-generated)

# GITLAB DOCS - .gitlab-ci.yml

## Inputs

|     Key     |           Value           | Description | Options  | Expand |
| :---------: | :-----------------------: | :---------: | :------: | :----: |
|  job-stage  |    {'default': 'test'}    |   &#x274c;  | &#x274c; |  true  |
| environment | {'default': 'production'} |   &#x274c;  | &#x274c; |  true  |


## Variables

|     Key     |     Value      | Description | Options  | Expand |
| :---------: | :------------: | :---------: | :------: | :----: |
| APPLICATION |  gitlab-docs   |   &#x274c;  | &#x274c; |  true  |
| OUTPUT_FILE | GITLAB-DOCS.md |   &#x274c;  | &#x274c; |  true  |

## Jobs
<h4><span class="badge text-bg-secondary">.TEST:RULES</span></h4>

<hr>

| **Attribute** |                       **Value**                       |
| :-----------: | :---------------------------------------------------: |
|   **rules**   | ['if': '$CI_PIPELINE_SOURCE == "merge_request_event"' |
|               |    'if': '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH']   |
|   **stage**   |                          test                         |

<h4><span class="badge text-bg-info">MEGALINTER</span></h4>

<hr>

|   **Attribute**   |           **Value**            |
| :---------------: | :----------------------------: |
| **allow_failure** |              True              |
|    **extends**    |        ['.test:rules']         |
|     **image**     | oxsecurity/megalinter-ci_light |

| <span class="badge text-bg-danger">Attribute</span> | <span class="badge text-bg-warning">Key</span> | <span class="badge text-bg-success">Value</span> |
| :-------------------------------------------------: | :--------------------------------------------: | :----------------------------------------------: |
|                      variables                      |               DEFAULT_WORKSPACE                |                 $CI_PROJECT_DIR                  |


<h4><span class="badge text-bg-info">BEHAVE-TESTS</span></h4>

<hr>

| **Attribute** |      **Value**      |
| :-----------: | :-----------------: |
|  **extends**  |    ['.test:rules'   |
|               |  '.poetry:install'] |

| <span class="badge text-bg-danger">Attribute</span> | <span class="badge text-bg-warning">Key</span> | <span class="badge text-bg-success">Value</span> |
| :-------------------------------------------------: | :--------------------------------------------: | :----------------------------------------------: |
|                      variables                      |           POETRY_VIRTUALENVS_CREATE            |                      false                       |


<h4><span class="badge text-bg-info">BUMP-VERSION</span></h4>

<hr>

| **Attribute** |               **Value**               |
| :-----------: | :-----------------------------------: |
|   **image**   |             python:3.12.11            |
|   **rules**   | ['if': '$CI_COMMIT_BRANCH == "main"'] |
|   **stage**   |                 .post                 |

<h4><span class="badge text-bg-secondary">.BUILD:PYTHON</span></h4>

<hr>

|  **Attribute**  |      **Value**      |
| :-------------: | :-----------------: |
| **environment** |       release       |
|   **extends**   | ['.poetry:install'] |
|    **stage**    |        build        |

<h4><span class="badge text-bg-info">TEST-BUILD</span></h4>

<hr>

| **Attribute** |     **Value**     |
| :-----------: | :---------------: |
|  **extends**  | ['.build:python'] |

<h4><span class="badge text-bg-info">PUBLISH</span></h4>

<hr>

| **Attribute** |                    **Value**                    |
| :-----------: | :---------------------------------------------: |
|  **extends**  |               ['.poetry:install']               |
| **id_tokens** |      'PYPI_JWT': 'aud': 'https://pypi.org'      |
|   **rules**   | ['if': '$CI_COMMIT_REF_NAME == $CI_COMMIT_TAG'] |
|   **stage**   |                     publish                     |

<h4><span class="badge text-bg-info">DOCKER-BUILD</span></h4>

<hr>

| **Attribute** |                    **Value**                    |
| :-----------: | :---------------------------------------------: |
|   **image**   |                  docker:latest                  |
|   **rules**   | ['if': '$CI_COMMIT_REF_NAME != $CI_COMMIT_TAG'] |
|  **services** |                 ['docker:dind']                 |
|   **stage**   |                      build                      |
|    **tags**   |              ['gitlab-org-docker']              |

[comment]: <> (gitlab-docs-closing-auto-generated)
