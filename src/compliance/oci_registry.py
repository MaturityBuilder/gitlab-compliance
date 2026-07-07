"""Push and pull GitLab compliance policy bundles to OCI registries."""

from __future__ import annotations

import os
import re
import shutil
import tempfile
from pathlib import Path

import oras.client
from oras.utils import extract_targz, make_targz

POLICY_BUNDLE_MEDIA_TYPE = "application/vnd.gitlab-compliance.policy.bundle.v1+tar+gzip"
OCI_SCHEME = "oci://"
DEFAULT_POLICY_DIR = "policy"
REGISTRY_REFERENCE = re.compile(
    r"^(?:oci://)?"
    r"(?:localhost(?::\d+)?|[\w.-]+\.[a-zA-Z]{2,})(?::\d+)?/"
)


def is_oci_reference(value: str) -> bool:
    if value.startswith(OCI_SCHEME):
        return True
    if os.path.isdir(value) or os.path.isfile(value):
        return False
    return bool(REGISTRY_REFERENCE.match(value))


def normalize_oci_reference(reference: str) -> str:
    reference = reference.strip()
    if reference.startswith(OCI_SCHEME):
        reference = reference[len(OCI_SCHEME) :]
    if ":" not in reference.split("/")[-1]:
        reference = f"{reference}:latest"
    return reference


def bundle_policies_dir(features_dir: str) -> str:
    if not os.path.isdir(features_dir):
        raise FileNotFoundError(f"Policies directory not found: {features_dir}")

    feature_files = list(Path(features_dir).rglob("*.feature"))
    if not feature_files:
        raise FileNotFoundError(f"No .feature files found in {features_dir}")

    bundle_path = os.path.join(tempfile.mkdtemp(prefix="gitlab-compliance-policy-bundle-"), "policies.tar.gz")
    return make_targz(features_dir, bundle_path)


def extract_policy_bundle(bundle_path: str, output_dir: str) -> str:
    os.makedirs(output_dir, exist_ok=True)
    extract_targz(bundle_path, output_dir)
    return os.path.abspath(output_dir)


def _client() -> oras.client.OrasClient:
    return oras.client.OrasClient()


def push_policies(features_dir: str, target: str) -> str:
    target = normalize_oci_reference(target)
    bundle_path = bundle_policies_dir(features_dir)
    bundle_dir = os.path.dirname(bundle_path)

    try:
        client = _client()
        response = client.push(
            target=target,
            files=[f"{bundle_path}:{POLICY_BUNDLE_MEDIA_TYPE}"],
            manifest_annotations={
                "org.opencontainers.image.title": "GitLab Docs compliance policies",
                "org.opencontainers.image.description": "Gherkin compliance policy bundle",
            },
        )
        digest = ""
        if hasattr(response, "json"):
            try:
                digest = response.json().get("digest", "")
            except Exception:
                digest = ""
        if digest:
            return digest
        return getattr(response, "reason", "pushed")
    finally:
        shutil.rmtree(bundle_dir, ignore_errors=True)


def pull_policies(target: str, output_dir: str | None = None) -> str:
    target = normalize_oci_reference(target)
    output_dir = os.path.abspath(output_dir or DEFAULT_POLICY_DIR)
    temp_root = tempfile.mkdtemp(prefix="gitlab-compliance-policy-pull-")

    try:
        client = _client()
        pulled_files = client.pull(
            target=target,
            outdir=temp_root,
            allowed_media_type=[POLICY_BUNDLE_MEDIA_TYPE, "application/vnd.oci.image.layer.v1.tar+gzip"],
            overwrite=True,
        )
        bundle_path = _find_bundle_file(temp_root, pulled_files)
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        os.makedirs(output_dir, exist_ok=True)
        extract_policy_bundle(bundle_path, output_dir)
        return output_dir
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


def _find_bundle_file(temp_root: str, pulled_files: list[str] | None) -> str:
    candidates: list[str] = []
    if pulled_files:
        candidates.extend(pulled_files)
    for root, _dirs, files in os.walk(temp_root):
        for filename in files:
            if filename.endswith(".tar.gz") or filename.endswith(".tgz"):
                candidates.append(os.path.join(root, filename))

    for candidate in candidates:
        if os.path.isfile(candidate):
            return candidate

    raise FileNotFoundError("Policy bundle not found in pulled OCI artifact.")


def resolve_features_dir(features_dir: str, cache_dir: str | None = None) -> str:
    if os.path.isdir(features_dir):
        return os.path.abspath(features_dir)

    if is_oci_reference(features_dir):
        cache_dir = cache_dir or os.path.join(tempfile.gettempdir(), "gitlab-compliance-policies")
        os.makedirs(cache_dir, exist_ok=True)
        return pull_policies(features_dir, output_dir=cache_dir)

    raise FileNotFoundError(
        f"Policies source not found: {features_dir}. "
        "Provide a local directory or an OCI reference such as oci://registry.example.com/policies:1.0.0"
    )
