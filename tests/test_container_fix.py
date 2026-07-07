from src.compliance.container_fix import (
    ContainerImageFix,
    apply_container_image_fixes,
    collect_container_image_fixes,
)

DIGEST = "66d292e5c26bd33a6f6f61cacb880de2186339a524ecba1ce098dbbaceed6515"


class TestCollectContainerImageFixes:
    def test_collects_digest_pin_candidates(self):
        entities = {
            "container_images": [
                {
                    "image": "python:3.12.0",
                    "latest_digest": "abc123",
                    "source_file": "ci.yml",
                    "line": 1,
                    "parent_job": "scan",
                    "image_source": "job",
                }
            ]
        }
        fixes = collect_container_image_fixes(entities)
        assert len(fixes) == 1
        assert fixes[0].fixed_image == "python@sha256:abc123"


class TestApplyContainerImageFixes:
    def test_patches_job_image_to_digest(self, tmp_path):
        pipeline = tmp_path / ".gitlab-ci.yml"
        pipeline.write_text(
            "scan:\n"
            "  image: python:3.12.0\n"
            "  script:\n"
            "    - echo scan\n",
            encoding="utf-8",
        )
        fixes = [
            ContainerImageFix(
                source_file=str(pipeline),
                line=1,
                parent_job="scan",
                image_source="job",
                current_image="python:3.12.0",
                fixed_image="python@sha256:abc123",
            )
        ]
        applied = apply_container_image_fixes(fixes)
        assert applied
        assert "python@sha256:abc123" in pipeline.read_text(encoding="utf-8")

    def test_does_not_replace_job_name_stage_or_script_when_image_is_docker(
        self, tmp_path
    ):
        pipeline = tmp_path / ".gitlab-ci.yml"
        pipeline.write_text(
            "docker:\n"
            "  stage: docker\n"
            "  image: docker\n"
            "  script:\n"
            "    - docker info\n",
            encoding="utf-8",
        )
        fixes = [
            ContainerImageFix(
                source_file=str(pipeline),
                line=1,
                parent_job="docker",
                image_source="job",
                current_image="docker",
                fixed_image=f"docker@sha256:{DIGEST}",
            )
        ]
        applied = apply_container_image_fixes(fixes)
        assert applied
        content = pipeline.read_text(encoding="utf-8")
        assert content.startswith("docker:\n")
        assert "  stage: docker\n" in content
        assert f"  image: docker@sha256:{DIGEST}\n" in content
        assert "    - docker info\n" in content

    def test_patches_job_image_and_service_without_collateral_damage(self, tmp_path):
        pipeline = tmp_path / ".gitlab-ci.yml"
        pipeline.write_text(
            "build:\n"
            "  image: docker:24.0.5\n"
            "  services:\n"
            "    - docker:24.0.5-dind\n"
            "  script:\n"
            "    - docker version\n",
            encoding="utf-8",
        )
        job_fix = ContainerImageFix(
            source_file=str(pipeline),
            line=1,
            parent_job="build",
            image_source="job",
            current_image="docker:24.0.5",
            fixed_image=f"docker@sha256:{DIGEST}",
        )
        service_fix = ContainerImageFix(
            source_file=str(pipeline),
            line=1,
            parent_job="build",
            image_source="service",
            current_image="docker:24.0.5-dind",
            fixed_image=f"docker@sha256:{'b' * 64}",
        )
        applied = apply_container_image_fixes([job_fix, service_fix])
        assert len(applied) == 2
        content = pipeline.read_text(encoding="utf-8")
        assert f"  image: docker@sha256:{DIGEST}\n" in content
        assert f"    - docker@sha256:{'b' * 64}\n" in content
        assert "    - docker version\n" in content

    def test_does_not_partially_match_registry_path(self, tmp_path):
        pipeline = tmp_path / ".gitlab-ci.yml"
        original = (
            "scan:\n"
            "  image: registry.example.com/docker/app:1.0\n"
            "  script:\n"
            "    - echo scan\n"
        )
        pipeline.write_text(original, encoding="utf-8")
        fixes = [
            ContainerImageFix(
                source_file=str(pipeline),
                line=1,
                parent_job="scan",
                image_source="job",
                current_image="docker",
                fixed_image=f"docker@sha256:{DIGEST}",
            )
        ]
        applied = apply_container_image_fixes(fixes)
        assert not applied
        assert pipeline.read_text(encoding="utf-8") == original

    def test_patches_quoted_image_value(self, tmp_path):
        pipeline = tmp_path / ".gitlab-ci.yml"
        pipeline.write_text(
            'scan:\n'
            '  image: "docker:latest"\n'
            "  script:\n"
            "    - echo scan\n",
            encoding="utf-8",
        )
        fixes = [
            ContainerImageFix(
                source_file=str(pipeline),
                line=1,
                parent_job="scan",
                image_source="job",
                current_image="docker:latest",
                fixed_image=f"docker@sha256:{DIGEST}",
            )
        ]
        applied = apply_container_image_fixes(fixes)
        assert applied
        assert f'  image: "docker@sha256:{DIGEST}"\n' in pipeline.read_text(
            encoding="utf-8"
        )
