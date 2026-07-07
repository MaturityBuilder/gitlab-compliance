from unittest.mock import patch

from src.compliance.image_versions import (
    enrich_container_images_with_releases,
    image_update_available,
    image_uses_sha256_digest,
    parse_container_image_ref,
)
from src.compliance.release_cache import ReleaseMetadataCache


class TestParseContainerImageRef:
    def test_parses_docker_hub_image_with_tag(self):
        parsed = parse_container_image_ref("python:3.12.0")
        assert parsed["repository"] == "library/python"
        assert parsed["tag"] == "3.12.0"

    def test_parses_digest_pinned_image(self):
        image = "python@sha256:" + ("a" * 64)
        assert image_uses_sha256_digest(image) is True
        parsed = parse_container_image_ref(image)
        assert parsed["digest"] == "a" * 64


class TestImageUpdateAvailable:
    def test_detects_outdated_semver_tag(self):
        assert image_update_available("3.12.0", "3.13.0") is True

    def test_detects_unpinned_latest(self):
        assert image_update_available("latest", "3.13.0") is True


class TestEnrichContainerImagesWithReleases:
    def test_list_docker_hub_tags_uses_cache_without_network(self):
        cache = ReleaseMetadataCache()
        cache.set_registry_tags("registry-1.docker.io", "library/python", ["3.12.0", "3.13.0"])

        with patch("src.compliance.image_versions.requests.get") as mock_get:
            from src.compliance.image_versions import _list_docker_hub_tags

            tags = _list_docker_hub_tags("library/python", cache=cache)

        mock_get.assert_not_called()
        assert tags == ["3.12.0", "3.13.0"]

    def test_enrich_reuses_cached_registry_tags_without_network(self):
        cache = ReleaseMetadataCache()
        cache.set_registry_tags(
            "registry-1.docker.io", "library/python", ["3.12.0", "3.13.0"]
        )
        cache.set_registry_digest(
            "registry-1.docker.io", "library/python", "3.12.0", "abc123"
        )
        cache.set_registry_digest(
            "registry-1.docker.io", "library/python", "3.13.0", "def456"
        )
        cache.set_docker_token("library/python", "fake-token")

        with patch("src.compliance.image_versions.requests.get") as mock_get:
            enriched = enrich_container_images_with_releases(
                [{"image": "python:3.12.0"}, {"image": "python:3.12.0"}],
                gitlab_url=None,
                token=None,
                cache=cache,
            )

        mock_get.assert_not_called()
        assert enriched[0]["release_metadata_resolved"] is True
        assert enriched[1]["release_metadata_resolved"] is True
