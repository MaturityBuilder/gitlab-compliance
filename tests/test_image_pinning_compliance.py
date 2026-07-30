"""Compliance integration tests for container image tag and digest pinning."""

from __future__ import annotations

from pathlib import Path

from src.compliance.runner import run_compliance
from src.compliance.stash import container_image_uses_sha256

REPO_ROOT = Path(__file__).resolve().parents[1]
IMAGE_PINNING_FEATURE = (
    REPO_ROOT / "examples" / "example-policies" / "security" / "image-pinning.feature"
)
DIGEST = (
    "python@sha256:66d292e5c26bd33a6f6f61cacb880de2186339a524ecba1ce098dbbaceed6515"
)


def _write_pipeline(tmp_path: Path, body: str) -> Path:
    pipeline = tmp_path / ".gitlab-ci.yml"
    pipeline.write_text(body, encoding="utf-8")
    return pipeline


class TestYamlImagePinning:
    def test_job_image_with_sha256_digest_passes_digest_policy(self, tmp_path):
        policies = tmp_path / "policies"
        policies.mkdir()
        policies.joinpath("image-pinning.feature").write_text(
            IMAGE_PINNING_FEATURE.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        pipeline = _write_pipeline(
            tmp_path,
            f"""\
stages:
  - test

digest-job:
  stage: test
  image: {DIGEST}
  script:
    - echo pinned
""",
        )
        result = run_compliance(
            features_dir=str(policies),
            pipeline_file=str(pipeline),
        )
        assert result.success is True

    def test_job_image_with_explicit_tag_passes_version_policy(self, tmp_path):
        policies = tmp_path / "policies"
        policies.mkdir()
        policies.joinpath("image-pinning.feature").write_text(
            (
                "# METADATA\n"
                "# custom:\n"
                "#   id: GLCI-BUILTIN-IMAGE-03\n"
                "Feature: Explicit image version\n\n"
                "  Scenario: Job images must include an explicit version or digest\n"
                "    Given I have any job defined\n"
                "    When it has image\n"
                '    Then its image must match "^[^\\s]+(:[\\w.-]+|@sha256:[a-f0-9]{64})$"\n'
            ),
            encoding="utf-8",
        )
        pipeline = _write_pipeline(
            tmp_path,
            """\
stages:
  - test

tag-job:
  stage: test
  image: python:3.12.0
  script:
    - echo tagged
""",
        )
        result = run_compliance(
            features_dir=str(policies),
            pipeline_file=str(pipeline),
        )
        assert result.success is True

    def test_bare_job_image_fails_digest_policy(self, tmp_path):
        policies = tmp_path / "policies"
        policies.mkdir()
        policies.joinpath("image-pinning.feature").write_text(
            (
                "# METADATA\n"
                "# custom:\n"
                "#   id: GLCI-BUILTIN-IMAGE-01\n"
                "Feature: Digest pinning\n\n"
                "  Scenario: Job images must use sha256 digest\n"
                '    Given I have container image from "job" defined\n'
                "    Then it must use sha256 digest\n"
            ),
            encoding="utf-8",
        )
        pipeline = _write_pipeline(
            tmp_path,
            """\
stages:
  - test

tag-only-job:
  stage: test
  image: python:3.12.0
  script:
    - echo tagged-only
""",
        )
        result = run_compliance(
            features_dir=str(policies),
            pipeline_file=str(pipeline),
        )
        assert result.success is False

    def test_container_image_predicate_distinguishes_tag_and_digest(self):
        assert container_image_uses_sha256({"image": DIGEST}) is True
        assert container_image_uses_sha256({"image": "python:3.12.0"}) is False
        assert container_image_uses_sha256({"image": "python"}) is False
