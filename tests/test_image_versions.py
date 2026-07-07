from unittest.mock import MagicMock, patch

from src.compliance.image_versions import (
    _docker_auth_token,
    _fetch_docker_hub_digest,
    _fetch_gitlab_registry_digest,
    _gitlab_registry_host,
    _latest_semver_tag,
    _list_docker_hub_tags,
    _list_gitlab_registry_tags,
    enrich_container_image_metadata,
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

    def test_returns_empty_for_blank_image(self):
        assert parse_container_image_ref("") == {}

    def test_parses_custom_registry_image(self):
        parsed = parse_container_image_ref("registry.example.com/org/app:1.0.0")
        assert parsed["registry"] == "registry.example.com"
        assert parsed["repository"] == "org/app"
        assert parsed["tag"] == "1.0.0"


class TestImageUpdateAvailable:
    def test_detects_outdated_semver_tag(self):
        assert image_update_available("3.12.0", "3.13.0") is True

    def test_detects_unpinned_latest(self):
        assert image_update_available("latest", "3.13.0") is True

    def test_rejects_empty_or_invalid_latest(self):
        assert image_update_available("3.12.0", "") is False
        assert image_update_available("3.12.0", "main") is False


class TestLatestSemverTag:
    def test_returns_none_without_semver_tags(self):
        assert _latest_semver_tag(["latest", "main"]) is None


class TestGitlabRegistryHost:
    def test_uses_gitlab_url_host(self, monkeypatch):
        monkeypatch.delenv("CI_SERVER_URL", raising=False)
        monkeypatch.delenv("GITLAB_URL", raising=False)
        assert _gitlab_registry_host("https://gitlab.example.com") == (
            "registry.gitlab.example.com"
        )


class TestDockerRegistryHelpers:
    def test_list_docker_hub_tags_uses_cache_without_network(self):
        cache = ReleaseMetadataCache()
        cache.set_registry_tags(
            "registry-1.docker.io", "library/python", ["3.12.0", "3.13.0"]
        )

        with patch("src.compliance.image_versions.requests.get") as mock_get:
            tags = _list_docker_hub_tags("library/python", cache=cache)

        mock_get.assert_not_called()
        assert tags == ["3.12.0", "3.13.0"]

    def test_docker_auth_token_uses_cache(self):
        cache = ReleaseMetadataCache()
        cache.set_docker_token("library/python", "cached-token")

        with patch("src.compliance.image_versions.requests.get") as mock_get:
            token = _docker_auth_token("library/python", cache=cache)

        mock_get.assert_not_called()
        assert token == "cached-token"

    def test_docker_auth_token_fetches_and_caches(self):
        cache = ReleaseMetadataCache()
        response = MagicMock()
        response.json.return_value = {"token": "fresh-token"}
        response.raise_for_status = MagicMock()

        with patch("src.compliance.image_versions.requests.get", return_value=response):
            token = _docker_auth_token("library/python", cache=cache)

        assert token == "fresh-token"
        assert cache.get_docker_token("library/python") == "fresh-token"

    def test_fetch_docker_hub_digest_uses_cache(self):
        cache = ReleaseMetadataCache()
        cache.set_registry_digest(
            "registry-1.docker.io", "library/python", "3.12.0", "abc123"
        )

        with patch("src.compliance.image_versions.requests.get") as mock_get:
            digest = _fetch_docker_hub_digest("library/python", "3.12.0", cache=cache)

        mock_get.assert_not_called()
        assert digest == "abc123"

    def test_list_docker_hub_tags_fetches_and_caches(self):
        cache = ReleaseMetadataCache()
        cache.set_docker_token("library/python", "token")
        response = MagicMock()
        response.json.return_value = {"tags": ["3.12.0"]}
        response.raise_for_status = MagicMock()

        with patch("src.compliance.image_versions.requests.get", return_value=response):
            tags = _list_docker_hub_tags("library/python", cache=cache)

        assert tags == ["3.12.0"]
        assert cache.get_registry_tags("registry-1.docker.io", "library/python") == [
            "3.12.0"
        ]

    def test_fetch_docker_hub_digest_fetches_and_caches(self):
        cache = ReleaseMetadataCache()
        cache.set_docker_token("library/python", "token")
        response = MagicMock()
        response.headers = {"Docker-Content-Digest": "sha256:deadbeef"}
        response.raise_for_status = MagicMock()

        with patch("src.compliance.image_versions.requests.get", return_value=response):
            digest = _fetch_docker_hub_digest("library/python", "3.12.0", cache=cache)

        assert digest == "deadbeef"
        assert (
            cache.get_registry_digest(
                "registry-1.docker.io", "library/python", "3.12.0"
            )
            == "deadbeef"
        )


class TestGitlabRegistryHelpers:
    def test_list_gitlab_registry_tags_uses_cache(self):
        cache = ReleaseMetadataCache()
        cache.set_registry_tags("registry.gitlab.example.com", "group/app", ["1.0.0"])

        with patch("src.compliance.image_versions.requests.get") as mock_get:
            tags = _list_gitlab_registry_tags(
                "group/app",
                gitlab_url="https://gitlab.example.com",
                token="secret",
                cache=cache,
            )

        mock_get.assert_not_called()
        assert tags == ["1.0.0"]

    def test_list_gitlab_registry_tags_fetches_and_caches(self):
        cache = ReleaseMetadataCache()
        response = MagicMock()
        response.json.return_value = {"tags": ["1.0.0", "1.1.0"]}
        response.raise_for_status = MagicMock()

        with patch("src.compliance.image_versions.requests.get", return_value=response):
            tags = _list_gitlab_registry_tags(
                "group/app",
                gitlab_url="https://gitlab.example.com",
                token="secret",
                cache=cache,
            )

        assert tags == ["1.0.0", "1.1.0"]
        assert cache.get_registry_tags("registry.gitlab.example.com", "group/app") == [
            "1.0.0",
            "1.1.0",
        ]

    def test_fetch_gitlab_registry_digest_uses_cache(self):
        cache = ReleaseMetadataCache()
        cache.set_registry_digest(
            "registry.gitlab.example.com", "group/app", "1.0.0", "abc123"
        )

        with patch("src.compliance.image_versions.requests.get") as mock_get:
            digest = _fetch_gitlab_registry_digest(
                "group/app",
                "1.0.0",
                gitlab_url="https://gitlab.example.com",
                token="secret",
                cache=cache,
            )

        mock_get.assert_not_called()
        assert digest == "abc123"

    def test_fetch_gitlab_registry_digest_fetches_and_caches(self):
        cache = ReleaseMetadataCache()
        response = MagicMock()
        response.headers = {"Docker-Content-Digest": "sha256:feedface"}
        response.raise_for_status = MagicMock()

        with patch("src.compliance.image_versions.requests.get", return_value=response):
            digest = _fetch_gitlab_registry_digest(
                "group/app",
                "1.0.0",
                gitlab_url="https://gitlab.example.com",
                token="secret",
                cache=cache,
            )

        assert digest == "feedface"
        assert (
            cache.get_registry_digest(
                "registry.gitlab.example.com", "group/app", "1.0.0"
            )
            == "feedface"
        )


class TestEnrichContainerImagesWithReleases:
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

    def test_enrich_returns_early_for_digest_pinned_image(self):
        digest = "a" * 64
        enriched = enrich_container_image_metadata(
            {"image": f"python@sha256:{digest}"},
            gitlab_url=None,
            token=None,
        )
        assert enriched["release_metadata_resolved"] is True
        assert enriched["digest"] == digest

    def test_enrich_uses_gitlab_registry_when_token_present(self):
        cache = ReleaseMetadataCache()
        cache.set_registry_tags(
            "registry.gitlab.example.com", "group/app", ["1.0.0", "1.1.0"]
        )
        cache.set_registry_digest(
            "registry.gitlab.example.com", "group/app", "1.0.0", "abc123"
        )
        cache.set_registry_digest(
            "registry.gitlab.example.com", "group/app", "1.1.0", "def456"
        )

        with patch("src.compliance.image_versions.requests.get") as mock_get:
            enriched = enrich_container_image_metadata(
                {"image": "registry.gitlab.example.com/group/app:1.0.0"},
                gitlab_url="https://gitlab.example.com",
                token="secret",
                cache=cache,
            )

        mock_get.assert_not_called()
        assert enriched["release_metadata_resolved"] is True
        assert enriched["latest_version"] == "1.1.0"

    def test_enrich_returns_early_for_unknown_registry(self):
        enriched = enrich_container_image_metadata(
            {"image": "unknown.registry.example.com/app:1.0.0"},
            gitlab_url=None,
            token=None,
        )
        assert enriched["release_metadata_resolved"] is False

    def test_enrich_swallows_registry_errors(self):
        with patch(
            "src.compliance.image_versions._list_docker_hub_tags",
            side_effect=RuntimeError("network down"),
        ):
            enriched = enrich_container_image_metadata(
                {"image": "python:3.12.0"},
                gitlab_url=None,
                token=None,
            )
        assert enriched["release_metadata_resolved"] is False

    def test_enrich_returns_when_no_latest_tag(self):
        with patch(
            "src.compliance.image_versions._list_docker_hub_tags",
            return_value=[],
        ):
            enriched = enrich_container_image_metadata(
                {"image": "python:3.12.0"},
                gitlab_url=None,
                token=None,
            )
        assert enriched["release_metadata_resolved"] is False
