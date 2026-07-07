"""Per-run cache for GitLab and registry release metadata."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ReleaseMetadataCache:
    gitlab_tag_dates: dict[tuple[str, str], dict[str, datetime]] = field(
        default_factory=dict
    )
    registry_tags: dict[tuple[str, str], list[str]] = field(default_factory=dict)
    registry_digests: dict[tuple[str, str, str], str] = field(default_factory=dict)
    docker_auth_tokens: dict[str, str] = field(default_factory=dict)

    def get_gitlab_tag_dates(
        self, gitlab_url: str, project_path: str
    ) -> dict[str, datetime] | None:
        return self.gitlab_tag_dates.get((gitlab_url, project_path))

    def set_gitlab_tag_dates(
        self, gitlab_url: str, project_path: str, tag_dates: dict[str, datetime]
    ) -> None:
        self.gitlab_tag_dates[(gitlab_url, project_path)] = tag_dates

    def get_registry_tags(self, registry: str, repository: str) -> list[str] | None:
        return self.registry_tags.get((registry, repository))

    def set_registry_tags(
        self, registry: str, repository: str, tags: list[str]
    ) -> None:
        self.registry_tags[(registry, repository)] = tags

    def get_registry_digest(
        self, registry: str, repository: str, tag: str
    ) -> str | None:
        digest = self.registry_digests.get((registry, repository, tag))
        return digest if digest is not None else None

    def set_registry_digest(
        self, registry: str, repository: str, tag: str, digest: str
    ) -> None:
        self.registry_digests[(registry, repository, tag)] = digest

    def get_docker_token(self, repository: str) -> str | None:
        return self.docker_auth_tokens.get(repository)

    def set_docker_token(self, repository: str, token: str) -> None:
        self.docker_auth_tokens[repository] = token
