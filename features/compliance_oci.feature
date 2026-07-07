Feature: Compliance OCI policy bundles
  As a platform engineer
  I want to store policies in an OCI registry
  So that teams can share versioned policy packs like Conftest

  Scenario: Policy bundle can be created and extracted locally
    When I bundle and extract policies from "examples/examples/example-policies/security" to "/tmp/gitlab-compliance-policy-bundle-test"
    Then the extracted policies directory should contain "image-pinning.feature"

  Scenario: OCI references are detected separately from local paths
    When I check whether "oci://registry.example.com/policies:1.0.0" is an OCI reference
    Then it should be an OCI reference
    When I check whether "examples/examples/example-policies/security" is an OCI reference
    Then it should not be an OCI reference
