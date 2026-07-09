# OCI Policy Packs

Publish and consume policy bundles from OCI-compliant registries (GitLab
Container Registry, GHCR, ACR, ECR), similar to [Conftest
sharing](https://www.conftest.dev/sharing/).

## Publish

```bash
docker login registry.example.com
gitlab-compliance policies push \
  -f policies/ \
  registry.example.com/org/gitlab-ci-policies:1.0.0
```

## Pull and run

```bash
gitlab-compliance policies pull \
  oci://registry.example.com/org/gitlab-ci-policies:1.0.0 \
  --output-dir policies/
gitlab-compliance check \
  -f oci://registry.example.com/org/gitlab-ci-policies:1.0.0 \
  -p .gitlab-ci.yml
gitlab-compliance check \
  -f oci://registry.example.com/org/gitlab-ci-policies:1.0.0 \
  -p .gitlab-ci.yml \
  --update
```

Bundles use media type
`application/vnd.gitlab-compliance.policy.bundle.v1+tar+gzip`.

## Policy catalog

Index policies with [Policy Metadata](../bdd-reference/metadata.md):

```bash
gitlab-compliance policies doc -f policies/ -o COMPLIANCE-POLICIES.md
```

## Consume in GitLab CI

Pull the latest bundle on every pipeline run:

```yaml
include:
  - local: example-ci/compliance-jobs.yml

compliance:
  extends: .compliance:oci
```

Override the registry reference:

```yaml
compliance:
  extends: .compliance:oci
  variables:
    COMPLIANCE_OCI: oci://registry.example.com/my-group/gitlab-ci-policies:2.0.0
```

Authenticate to the registry in `before_script` when using a private registry:

```yaml
compliance:
  extends: .compliance:oci
  before_script:
    - echo "$CI_REGISTRY_PASSWORD" | docker login -u "$CI_REGISTRY_USER"
      --password-stdin $CI_REGISTRY
    - pip install --quiet gitlab-compliance
```

## Run locally

```bash
gitlab-compliance check \
  -f oci://registry.example.com/org/gitlab-ci-policies:1.0.0 \
  -p .gitlab-ci.yml --update
```

Back to [Examples](index.md).
