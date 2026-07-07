"""Container image version validation and registry metadata."""

from __future__ import annotations

import os
from urllib.parse import urlparse

import requests
import semver

from src.compliance.include_versions import (
    _semver_tags_descending,
    compute_version_tag_rank,
    is_valid_semver_version,
)
from src.compliance.release_cache import ReleaseMetadataCache


def parse_container_image_ref(image: str) -> dict[str, str]:
    image = str(image or "").strip()
    if not image:
        return {}

    digest = ""
    repository_part = image
    if "@sha256:" in image:
        repository_part, digest_value = image.split("@sha256:", 1)
        digest = digest_value.strip()

    registry = "registry-1.docker.io"
    repository = repository_part
    tag = "latest"

    if "/" in repository_part and "." in repository_part.split("/", 1)[0]:
        registry, repository = repository_part.split("/", 1)

    if ":" in repository:
        repository, tag = repository.rsplit(":", 1)

    if "/" not in repository and registry in {
        "registry-1.docker.io",
        "docker.io",
        "index.docker.io",
    }:
        repository = f"library/{repository}"

    return {
        "registry": registry,
        "repository": repository,
        "tag": tag,
        "digest": digest,
        "image": image,
    }


def image_uses_sha256_digest(image: str) -> bool:
    return "@sha256:" in str(image or "")


def _docker_auth_token(
    repository: str, cache: ReleaseMetadataCache | None = None
) -> str:
    if cache is not None:
        cached = cache.get_docker_token(repository)
        if cached:
            return cached

    response = requests.get(
        "https://auth.docker.io/token",
        params={
            "service": "registry.docker.io",
            "scope": f"repository:{repository}:pull",
        },
        timeout=30,
    )
    response.raise_for_status()
    token = response.json()["token"]
    if cache is not None:
        cache.set_docker_token(repository, token)
    return token


def _list_docker_hub_tags(
    repository: str, cache: ReleaseMetadataCache | None = None
) -> list[str]:
    registry = "registry-1.docker.io"
    if cache is not None:
        cached = cache.get_registry_tags(registry, repository)
        if cached is not None:
            return cached

    token = _docker_auth_token(repository, cache=cache)
    response = requests.get(
        f"https://registry-1.docker.io/v2/{repository}/tags/list",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    response.raise_for_status()
    tags = list(response.json().get("tags") or [])
    if cache is not None:
        cache.set_registry_tags(registry, repository, tags)
    return tags


def _fetch_docker_hub_digest(
    repository: str, tag: str, cache: ReleaseMetadataCache | None = None
) -> str:
    registry = "registry-1.docker.io"
    if cache is not None:
        cached = cache.get_registry_digest(registry, repository, tag)
        if cached is not None:
            return cached

    token = _docker_auth_token(repository, cache=cache)
    response = requests.get(
        f"https://registry-1.docker.io/v2/{repository}/manifests/{tag}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.docker.distribution.manifest.v2+json",
        },
        timeout=30,
    )
    response.raise_for_status()
    digest = response.headers.get("Docker-Content-Digest", "")
    digest_value = digest.split(":", 1)[1] if digest.startswith("sha256:") else ""
    if cache is not None:
        cache.set_registry_digest(registry, repository, tag, digest_value)
    return digest_value


def _gitlab_registry_host(gitlab_url: str | None) -> str:
    gitlab_url = (
        gitlab_url
        or os.getenv("CI_SERVER_URL")
        or os.getenv("GITLAB_URL")
        or "https://gitlab.com"
    )
    host = urlparse(gitlab_url).netloc or "gitlab.com"
    return f"registry.{host}"


def _list_gitlab_registry_tags(
    repository: str,
    *,
    gitlab_url: str | None,
    token: str,
    cache: ReleaseMetadataCache | None = None,
) -> list[str]:
    registry_host = _gitlab_registry_host(gitlab_url)
    if cache is not None:
        cached = cache.get_registry_tags(registry_host, repository)
        if cached is not None:
            return cached

    response = requests.get(
        f"https://{registry_host}/v2/{repository}/tags/list",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    response.raise_for_status()
    tags = list(response.json().get("tags") or [])
    if cache is not None:
        cache.set_registry_tags(registry_host, repository, tags)
    return tags


def _fetch_gitlab_registry_digest(
    repository: str,
    tag: str,
    *,
    gitlab_url: str | None,
    token: str,
    cache: ReleaseMetadataCache | None = None,
) -> str:
    registry_host = _gitlab_registry_host(gitlab_url)
    if cache is not None:
        cached = cache.get_registry_digest(registry_host, repository, tag)
        if cached is not None:
            return cached

    response = requests.get(
        f"https://{registry_host}/v2/{repository}/manifests/{tag}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.docker.distribution.manifest.v2+json",
        },
        timeout=30,
    )
    response.raise_for_status()
    digest = response.headers.get("Docker-Content-Digest", "")
    digest_value = digest.split(":", 1)[1] if digest.startswith("sha256:") else ""
    if cache is not None:
        cache.set_registry_digest(registry_host, repository, tag, digest_value)
    return digest_value


def _latest_semver_tag(tag_names: list[str]) -> str | None:
    valid = [name for name in tag_names if is_valid_semver_version(name)]
    if not valid:
        return None
    return max(valid, key=lambda value: semver.Version.parse(value))


def image_update_available(current_tag: str, latest_tag: str) -> bool:
    if not latest_tag:
        return False
    current = str(current_tag or "").strip()
    if current in {"", "latest"} or not is_valid_semver_version(current):
        return is_valid_semver_version(latest_tag)
    if not is_valid_semver_version(latest_tag):
        return False
    return semver.Version.parse(latest_tag) > semver.Version.parse(current)


def enrich_container_image_metadata(
    image_entity: dict,
    *,
    gitlab_url: str | None,
    token: str | None,
    cache: ReleaseMetadataCache | None = None,
) -> dict:
    enriched = dict(image_entity)
    image_ref = str(enriched.get("image", enriched.get("project", ""))).strip()
    parsed = parse_container_image_ref(image_ref)
    enriched["image"] = image_ref
    enriched["registry"] = parsed.get("registry", "")
    enriched["repository"] = parsed.get("repository", "")
    enriched["version"] = parsed.get("tag", "")
    enriched["digest"] = parsed.get("digest", "")
    enriched["valid_version"] = is_valid_semver_version(enriched["version"])
    enriched["latest_version"] = ""
    enriched["latest_digest"] = ""
    enriched["update_available"] = False
    enriched["release_metadata_resolved"] = False
    enriched["latest_release_age_days"] = None
    enriched["release_lag_days"] = None
    enriched["version_tag_rank"] = None
    enriched["semver_tag_count"] = 0

    if image_uses_sha256_digest(image_ref):
        enriched["release_metadata_resolved"] = bool(enriched["digest"])
        return enriched

    repository = enriched.get("repository", "")
    tag = enriched.get("version", "latest")
    registry = enriched.get("registry", "")
    tags: list[str] = []
    latest_tag = ""
    latest_digest = ""

    try:
        if registry in {"registry-1.docker.io", "docker.io", "index.docker.io"}:
            tags = _list_docker_hub_tags(repository, cache=cache)
            latest_tag = _latest_semver_tag(tags) or (
                "latest" if "latest" in tags else (tags[0] if tags else "")
            )
            latest_digest = _fetch_docker_hub_digest(repository, tag, cache=cache)
            if latest_tag and latest_tag != tag:
                enriched["latest_digest"] = _fetch_docker_hub_digest(
                    repository, latest_tag, cache=cache
                )
        elif registry == _gitlab_registry_host(gitlab_url) and token:
            tags = _list_gitlab_registry_tags(
                repository, gitlab_url=gitlab_url, token=token, cache=cache
            )
            latest_tag = _latest_semver_tag(tags) or (
                "latest" if "latest" in tags else (tags[0] if tags else "")
            )
            latest_digest = _fetch_gitlab_registry_digest(
                repository, tag, gitlab_url=gitlab_url, token=token, cache=cache
            )
            if latest_tag and latest_tag != tag:
                enriched["latest_digest"] = _fetch_gitlab_registry_digest(
                    repository,
                    latest_tag,
                    gitlab_url=gitlab_url,
                    token=token,
                    cache=cache,
                )
        else:
            return enriched
    except Exception:
        return enriched

    if not latest_tag:
        return enriched

    tags_desc = _semver_tags_descending(
        [name for name in tags if is_valid_semver_version(name)]
    )
    enriched["latest_version"] = latest_tag
    enriched["latest_digest"] = latest_digest or enriched.get("latest_digest", "")
    enriched["update_available"] = image_update_available(tag, latest_tag)
    enriched["release_metadata_resolved"] = True
    enriched["semver_tag_count"] = len(tags_desc)
    if enriched["valid_version"]:
        enriched["version_tag_rank"] = compute_version_tag_rank(tag, tags_desc)
    return enriched


def enrich_container_images_with_releases(
    images: list[dict],
    *,
    gitlab_url: str | None,
    token: str | None,
    cache: ReleaseMetadataCache | None = None,
) -> list[dict]:
    return [
        enrich_container_image_metadata(
            image,
            gitlab_url=gitlab_url,
            token=token or "",
            cache=cache,
        )
        for image in images
    ]
