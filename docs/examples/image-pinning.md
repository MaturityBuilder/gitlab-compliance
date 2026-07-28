# Image Pinning

<p class="example-badges">
  <a class="example-badge example-badge--check" href="../usage/reference/check.md">check</a>
  <a class="example-badge example-badge--supply-chain" href="../usage/reference/check.md#fix-supply-chain">supply-chain</a>
</p>

Prevent jobs from using mutable or unpinned container images. **Sha256 digest
pinning** is the recommended default for supply-chain security.

## Bad

```yaml
scan:
  image: python
build:
  image: docker:latest
```

## Good (sha256 digest — default)

```yaml
scan:
  image:
  python@sha256:826cce1bda4ecb1d8a6ce203ac1b519660ba85e808e1306a43a908f49f90f341
build:
  image:
  docker@sha256:61394709d9c9999b6b7d6d5b8c7c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8
```

## Good (explicit semver tag)

```yaml
scan:
  image: python:3.12.11
build:
  image: docker:24.0.5
```

## Policy

From
[`security/image-pinning.feature`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/examples/example-policies/security/image-pinning.feature):

```gherkin
Scenario: Job images must use sha256 digest
  Given I have container image from "job" defined
  Then it must use sha256 digest

Scenario: Job images must not use the latest tag
  Given I have any job defined
  When it has image
  Then its image must not match ":latest$"

Scenario: Container images must not lag behind registry latest
  Given I have any container image with release metadata defined
  Then a newer image release must not be available
```

Registry-backed checks resolve tags from Docker Hub (public images) and GitLab
Container Registry (when the image host matches your GitLab instance).

## Auto-fix (`--fix-supply-chain`)

Pin job and service images to sha256 digests for the currently referenced tag:

```bash
gitlab-compliance check -f policies/security/ -p .gitlab-ci.yml --fix-supply-chain
```

## Consume in GitLab CI

Offline policy — use the shared compliance job templates from
[`example-ci/compliance-jobs.yml`](https://github.com/MaturityBuilder/gitlab-compliance/blob/main/example-ci/compliance-jobs.yml):

```yaml
include:
  - local: example-ci/compliance-jobs.yml

compliance:
  extends: .compliance:offline
```

Registry checks with API enrichment:

```yaml
compliance:
  extends: .compliance:api
```

Or apply fixes in CI:

```yaml
compliance:
  extends: .compliance:api
  script:
    - pip install --quiet gitlab-compliance
    - gitlab-compliance check -f "$COMPLIANCE_POLICIES" -p .gitlab-ci.yml
        --project "$CI_PROJECT_PATH" --strict --fix-supply-chain
```

## Run locally

```bash
cp -r examples/example-policies/security/ policies/security/
gitlab-compliance check -f policies/security/ -p .gitlab-ci.yml
```

Back to [Examples](index.md).
