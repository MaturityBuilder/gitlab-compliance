# sbom

Write a CycloneDX SBOM for images, includes, and script packages.

    The manifest records the versions declared in GitLab CI YAML. Pass --resolve
    to add the digest, commit SHA, or file hash of that same pin. This command
    does not modify the pipeline file.

<!-- MANUAL DOCS:START -->

## What it writes

`gitlab-compliance sbom` writes a CycloneDX 1.6 JSON bill of materials for the
supply-chain components a GitLab pipeline declares:

- `include` entries (project, component, remote, template, local, and generated
  child artifacts)
- container images from jobs, `services`, `extends`, `default`, and `docker pull`
  or `docker run` in scripts
- packages installed from `before_script`, `script`, and `after_script`

Each component keeps the version written in the YAML. This command does not
upgrade pins and does not edit the pipeline. Use
[`supply-chain --fix`](supply-chain.md) when you want to update pins.

## Resolve immutable ids

Offline is the default. Pass `--resolve` to add the immutable id of the pin
that is already written:

- container images: digest of the declared tag (Docker Hub and the GitLab
  container registry)
- project includes: commit SHA for the declared ref, plus a hash of the fetched
  file
- remote and local includes: SHA-256 of the fetched body or local file

Unresolved components stay in the document with the declared version and no
hash. Component and template includes keep the identity from the YAML.

GitLab lists these components when the job publishes a CycloneDX report.
Vulnerability matching still depends on GitLab understanding the purl type.

## Publish in GitLab

```yaml
pipeline-sbom:
  image: python:3.12
  script:
    - pip install gitlab-compliance
    - gitlab-compliance sbom -p .gitlab-ci.yml
        --project "$CI_PROJECT_PATH"
        --resolve
        -o gl-sbom.cdx.json
  artifacts:
    reports:
      cyclonedx: gl-sbom.cdx.json
```

`--resolve` needs `GITLAB_TOKEN` or `CI_JOB_TOKEN` for project include commits
and GitLab registry digests. The report is still written when resolution is
unavailable.

<!-- MANUAL DOCS:END -->



## Usage

```
Usage: gitlab-compliance sbom [OPTIONS]
```

## Options
* `pipeline_file`:
  * Type: STRING
  * Default: `.gitlab-ci.yml`
  * Usage: `--pipeline
-p`

  Path to the GitLab CI pipeline YAML file.

* `output_file`:
  * Type: STRING
  * Default: `none`
  * Usage: `--output-file
-o`

  Write the CycloneDX JSON to this file (default: stdout).

* `include_nested`:
  * Type: BOOL
  * Default: `true`
  * Usage: `--include-nested`

  Resolve nested local include files into the inventory.

* `max_include_depth`:
  * Type: INT
  * Default: `none`
  * Usage: `--max-include-depth`

  Max local include nesting depth from the root file (omit for unlimited).

* `resolve_external_includes`:
  * Type: BOOL
  * Default: `none`
  * Usage: `--resolve-external-includes`

  Fetch remote and project include YAML (default: auto — remote always, project when a token is available).

* `resolve_generated`:
  * Type: BOOL
  * Default: `true`
  * Usage: `--resolve-generated`

  Load dynamically generated child pipeline YAML from trigger.include artifact paths when the file exists on disk (default: on).

* `generated_configs`:
  * Type: STRING
  * Default: `sentinel.unset`
  * Usage: `--generated-config`

  Extra generated CI YAML path to merge (repeatable). Use when the artifact is written somewhere other than the declared trigger.include path.

* `gitlab_url`:
  * Type: STRING
  * Default: `none`
  * Usage: `--gitlab-url`

  GitLab instance URL (default: CI_SERVER_URL or https://gitlab.com).

* `token`:
  * Type: STRING
  * Default: `none`
  * Usage: `--token`

  GitLab API token (default: GITLAB_TOKEN or CI_JOB_TOKEN).

* `project`:
  * Type: STRING
  * Default: `none`
  * Usage: `--project`

  GitLab project path recorded on the SBOM metadata.

* `resolve`:
  * Type: BOOL
  * Default: `false`
  * Usage: `--resolve`

  Resolve the digest, commit SHA, or file hash of each pin as written. Does not upgrade versions and does not modify the pipeline file.

* `_click_default_help`:
  * Type: BOOL
  * Default: `sentinel.unset`
  * Usage: `--help`

  Show this message and exit.


## CLI Help

```
Usage: gitlab-compliance sbom [OPTIONS]

  Write a CycloneDX SBOM for images, includes, and script packages.

  The manifest records the versions declared in GitLab CI YAML. Pass --resolve
  to add the digest, commit SHA, or file hash of that same pin. This command
  does not modify the pipeline file.

Options:
  -p, --pipeline TEXT             Path to the GitLab CI pipeline YAML file.
  -o, --output-file TEXT          Write the CycloneDX JSON to this file
                                  (default: stdout).
  --include-nested / --no-include-nested
                                  Resolve nested local include files into the
                                  inventory.
  --max-include-depth INTEGER     Max local include nesting depth from the
                                  root file (omit for unlimited).
  --resolve-external-includes / --no-resolve-external-includes
                                  Fetch remote and project include YAML
                                  (default: auto — remote always, project when
                                  a token is available).
  --resolve-generated / --no-resolve-generated
                                  Load dynamically generated child pipeline
                                  YAML from trigger.include artifact paths
                                  when the file exists on disk (default: on).
  --generated-config TEXT         Extra generated CI YAML path to merge
                                  (repeatable). Use when the artifact is
                                  written somewhere other than the declared
                                  trigger.include path.
  --gitlab-url TEXT               GitLab instance URL (default: CI_SERVER_URL
                                  or https://gitlab.com).
  --token TEXT                    GitLab API token (default: GITLAB_TOKEN or
                                  CI_JOB_TOKEN).
  --project TEXT                  GitLab project path recorded on the SBOM
                                  metadata.
  --resolve / --no-resolve        Resolve the digest, commit SHA, or file hash
                                  of each pin as written. Does not upgrade
                                  versions and does not modify the pipeline
                                  file.
  --help                          Show this message and exit.
```
