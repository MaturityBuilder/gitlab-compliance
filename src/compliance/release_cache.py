"""Per-run cache for GitLab and registry release metadata."""

from __future__ import annotations

import threading
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
    _lock: threading.Lock = field(
        default_factory=threading.Lock, repr=False, compare=False
    )

    def get_gitlab_tag_dates(
        self, gitlab_url: str, project_path: str
    ) -> dict[str, datetime] | None:
        with self._lock:
            return self.gitlab_tag_dates.get((gitlab_url, project_path))

    def set_gitlab_tag_dates(
        self, gitlab_url: str, project_path: str, tag_dates: dict[str, datetime]
    ) -> None:
        with self._lock:
            self.gitlab_tag_dates[(gitlab_url, project_path)] = tag_dates

    def get_registry_tags(self, registry: str, repository: str) -> list[str] | None:
        with self._lock:
            return self.registry_tags.get((registry, repository))

    def set_registry_tags(
        self, registry: str, repository: str, tags: list[str]
    ) -> None:
        with self._lock:
            self.registry_tags[(registry, repository)] = tags

    def get_registry_digest(
        self, registry: str, repository: str, tag: str
    ) -> str | None:
        with self._lock:
            digest = self.registry_digests.get((registry, repository, tag))
        return digest if digest is not None else None

    def set_registry_digest(
        self, registry: str, repository: str, tag: str, digest: str
    ) -> None:
        with self._lock:
            self.registry_digests[(registry, repository, tag)] = digest

    def get_docker_token(self, repository: str) -> str | None:
        with self._lock:
            return self.docker_auth_tokens.get(repository)

    def set_docker_token(self, repository: str, token: str) -> None:
        with self._lock:
            self.docker_auth_tokens[repository] = token
