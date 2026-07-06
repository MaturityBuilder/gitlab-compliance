import os
import tempfile
from pathlib import Path

import pytest

from src.compliance.oci_registry import (
    bundle_policies_dir,
    extract_policy_bundle,
    is_oci_reference,
    normalize_oci_reference,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PASSING_POLICIES = REPO_ROOT / "tests" / "compliance_policies" / "passing"


class TestOciReferenceDetection:
    def test_oci_scheme(self):
        assert is_oci_reference("oci://registry.example.com/policies:1.0.0")

    def test_local_directory_is_not_oci(self):
        assert not is_oci_reference(str(PASSING_POLICIES))

    def test_registry_host_without_scheme(self):
        assert is_oci_reference("registry.example.com/org/policies:1.0.0")


class TestNormalizeOciReference:
    def test_strips_oci_prefix(self):
        assert (
            normalize_oci_reference("oci://registry.example.com/policies")
            == "registry.example.com/policies:latest"
        )

    def test_adds_latest_tag_when_missing(self):
        assert (
            normalize_oci_reference("registry.example.com/org/policies")
            == "registry.example.com/org/policies:latest"
        )


class TestPolicyBundle:
    def test_bundle_and_extract_round_trip(self):
        bundle_path = bundle_policies_dir(str(PASSING_POLICIES))
        assert os.path.isfile(bundle_path)
        with tempfile.TemporaryDirectory() as tmp:
            extracted = extract_policy_bundle(bundle_path, tmp)
            assert any(Path(extracted).rglob("*.feature"))

    def test_missing_directory_raises(self):
        with pytest.raises(FileNotFoundError):
            bundle_policies_dir("/nonexistent/policies")
