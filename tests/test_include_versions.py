from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from src.compliance.include_versions import (
    _latest_semver_tag,
    _semver_tags_descending,
    _tag_committed_date,
    compute_latest_release_age_days,
    compute_release_lag_days,
    compute_version_tag_rank,
    days_between,
    enrich_include_release_metadata,
    enrich_includes_with_releases,
    fetch_latest_semver_version,
    fetch_semver_tag_dates,
    include_update_available,
    is_valid_semver_version,
    resolve_include_project_path,
    version_within_latest_tags,
)
from src.compliance.model import load_yaml_entities
from src.compliance.stash import (
    include_newer_release_older_than_days,
    include_not_within_latest_tags,
    include_release_lag_exceeds_days,
    include_within_latest_tags,
)


def _tag(name: str, committed_date: str = "2024-01-01T00:00:00Z"):
    return SimpleNamespace(name=name, commit={"committed_date": committed_date})


class TestSemverValidation:
    def test_accepts_valid_semver(self):
        assert is_valid_semver_version("1.2.3") is True
        assert is_valid_semver_version("1.2.3-rc.1") is True

    def test_rejects_branch_names(self):
        assert is_valid_semver_version("main") is False
        assert is_valid_semver_version("") is False

    def test_rejects_invalid_semver_on_exception(self, monkeypatch):
        def boom(_version):
            raise RuntimeError("semver broken")

        monkeypatch.setattr(
            "src.compliance.include_versions.semver.Version.is_valid",
            boom,
        )
        assert is_valid_semver_version("1.0.0") is False


class TestResolveIncludeProjectPath:
    def test_project_include_uses_path_directly(self):
        assert resolve_include_project_path("project", "platform/ci-templates") == (
            "platform/ci-templates"
        )

    def test_component_include_strips_host(self):
        assert (
            resolve_include_project_path("component", "gitlab.com/org/pipeline")
            == "org/pipeline"
        )

    def test_component_include_strips_url(self):
        assert (
            resolve_include_project_path("component", "https://gitlab.com/org/pipeline")
            == "org/pipeline"
        )

    def test_local_include_returns_none(self):
        assert resolve_include_project_path("local", "ci/child.yml") is None

    def test_empty_project_path_returns_none(self):
        assert resolve_include_project_path("project", "") is None

    def test_strips_git_suffix(self):
        assert (
            resolve_include_project_path("project", "https://gitlab.com/org/repo.git")
            == "org/repo"
        )


class TestReleaseComparison:
    def test_detects_newer_release(self):
        assert include_update_available("1.0.0", "1.1.0") is True
        assert include_update_available("1.1.0", "1.1.0") is False
        assert include_update_available("main", "1.1.0") is True

    def test_rejects_empty_or_invalid_latest(self):
        assert include_update_available("1.0.0", "") is False
        assert include_update_available("1.0.0", "main") is False


class TestDayCalculations:
    def test_days_between_same_day_is_zero(self):
        start = datetime(2024, 6, 1, 12, 0, tzinfo=timezone.utc)
        end = datetime(2024, 6, 1, 23, 59, tzinfo=timezone.utc)
        assert days_between(start, end) == 0

    def test_compute_release_lag_days(self):
        pinned = datetime(2024, 1, 1, tzinfo=timezone.utc)
        latest = datetime(2024, 4, 1, tzinfo=timezone.utc)
        assert compute_release_lag_days(pinned, latest) == 91

    def test_compute_latest_release_age_days(self):
        latest = datetime(2024, 1, 1, tzinfo=timezone.utc)
        now = datetime(2024, 2, 1, tzinfo=timezone.utc)
        assert compute_latest_release_age_days(latest, now=now) == 31

    def test_compute_helpers_return_none_for_missing_dates(self):
        assert compute_release_lag_days(None, datetime.now(timezone.utc)) is None
        assert compute_latest_release_age_days(None) is None


class TestStashAgePredicates:
    def test_grace_predicate_requires_update_and_age(self):
        entity = {
            "update_available": True,
            "latest_release_age_days": 45,
        }
        assert include_newer_release_older_than_days(entity, 30) is True
        assert include_newer_release_older_than_days(entity, 45) is False
        assert (
            include_newer_release_older_than_days(
                {"update_available": False, "latest_release_age_days": 45}, 30
            )
            is False
        )

    def test_lag_predicate_requires_update_and_lag(self):
        entity = {
            "update_available": True,
            "release_lag_days": 120,
        }
        assert include_release_lag_exceeds_days(entity, 90) is True
        assert include_release_lag_exceeds_days(entity, 120) is False


class TestTagRank:
    def test_semver_tags_descending(self):
        tags = _semver_tags_descending(["1.0.0", "2.0.0", "1.2.0", "main"])
        assert tags == ["2.0.0", "1.2.0", "1.0.0"]

    def test_version_within_latest_tags(self):
        tags = ["2.0.0", "1.2.0", "1.1.0", "1.0.0"]
        assert version_within_latest_tags("2.0.0", tags, 1) is True
        assert version_within_latest_tags("1.2.0", tags, 3) is True
        assert version_within_latest_tags("1.0.0", tags, 3) is False
        assert version_within_latest_tags("9.9.9", tags, 3) is False

    def test_compute_version_tag_rank(self):
        tags = ["2.0.0", "1.2.0", "1.0.0"]
        assert compute_version_tag_rank("2.0.0", tags) == 1
        assert compute_version_tag_rank("1.0.0", tags) == 3
        assert compute_version_tag_rank("0.9.0", tags) is None


class TestStashTagRankPredicates:
    def test_within_latest_tags_predicate(self):
        entity = {"release_metadata_resolved": True, "version_tag_rank": 2}
        assert include_within_latest_tags(entity, 3) is True
        assert include_within_latest_tags(entity, 1) is False

    def test_not_within_latest_tags_predicate(self):
        entity = {"release_metadata_resolved": True, "version_tag_rank": 4}
        assert include_not_within_latest_tags(entity, 3) is True
        assert include_not_within_latest_tags(entity, 4) is False


class TestFetchLatestSemverVersion:
    def test_returns_highest_semver_tag(self):
        project = MagicMock()
        project.tags.list.return_value = [
            _tag("1.0.0"),
            _tag("1.2.0"),
            _tag("main"),
        ]
        gl = MagicMock()
        gl.projects.get.return_value = project

        assert fetch_latest_semver_version(gl, "platform/ci-templates") == "1.2.0"

    def test_latest_semver_tag_returns_none_without_semver_tags(self):
        assert _latest_semver_tag(["main", "develop"]) is None


class TestTagCommittedDate:
    def test_reads_commit_object_and_invalid_dates(self):
        tag = SimpleNamespace(
            name="1.0.0", commit=SimpleNamespace(committed_date="bad")
        )
        assert _tag_committed_date(tag) is None

        tag = SimpleNamespace(name="1.0.0", commit={"committed_date": "bad-date"})
        assert _tag_committed_date(tag) is None

        tag = SimpleNamespace(name="1.0.0", commit={})
        assert _tag_committed_date(tag) is None

        tag = _tag("1.0.0", "2024-01-01T00:00:00Z")
        assert _tag_committed_date(tag) is not None


class TestEnrichIncludeReleaseMetadata:
    def test_enriches_project_include_when_api_succeeds(self):
        include = {
            "include_type": "project",
            "project": "platform/ci-templates",
            "version": "1.0.0",
            "valid_version": True,
        }
        project = MagicMock()
        project.tags.list.return_value = [
            _tag("1.0.0", "2024-01-01T00:00:00Z"),
            _tag("1.2.0", "2024-06-01T00:00:00Z"),
        ]
        gl = MagicMock()
        gl.projects.get.return_value = project

        with patch("gitlab.Gitlab", return_value=gl):
            enriched = enrich_include_release_metadata(
                include,
                gitlab_url="https://gitlab.example.com",
                token="secret",
            )

        assert enriched["latest_version"] == "1.2.0"
        assert enriched["update_available"] is True
        assert enriched["release_metadata_resolved"] is True
        assert enriched["version_released_at"] != ""
        assert enriched["latest_version_released_at"] != ""
        assert enriched["release_lag_days"] == 152
        assert enriched["latest_release_age_days"] is not None
        assert enriched["version_tag_rank"] == 2
        assert enriched["semver_tag_count"] == 2

    def test_enriches_age_fields_when_up_to_date(self):
        include = {
            "include_type": "project",
            "project": "platform/ci-templates",
            "version": "1.2.0",
        }
        project = MagicMock()
        project.tags.list.return_value = [
            _tag("1.2.0", "2024-06-01T00:00:00Z"),
        ]
        gl = MagicMock()
        gl.projects.get.return_value = project

        with patch("gitlab.Gitlab", return_value=gl):
            enriched = enrich_include_release_metadata(
                include,
                gitlab_url="https://gitlab.example.com",
                token="secret",
            )

        assert enriched["update_available"] is False
        assert enriched["release_lag_days"] is None

    def test_enriches_latest_version_for_invalid_semver_ref(self):
        include = {
            "include_type": "project",
            "project": "platform/ci-templates",
            "version": "main",
        }
        project = MagicMock()
        project.tags.list.return_value = [_tag("2.0.0")]
        gl = MagicMock()
        gl.projects.get.return_value = project

        with patch("gitlab.Gitlab", return_value=gl) as gitlab_cls:
            enriched = enrich_include_release_metadata(
                include,
                gitlab_url="https://gitlab.example.com",
                token="secret",
            )

        gitlab_cls.assert_called_once()
        assert enriched["valid_version"] is False
        assert enriched["latest_version"] == "2.0.0"
        assert enriched["update_available"] is True
        assert enriched["release_metadata_resolved"] is True

    def test_returns_early_when_project_path_unresolved(self):
        enriched = enrich_include_release_metadata(
            {"include_type": "local", "project": "ci/child.yml", "version": "main"},
            gitlab_url="https://gitlab.example.com",
            token="secret",
        )
        assert enriched["release_metadata_resolved"] is False

    def test_returns_early_when_api_raises(self):
        gl = MagicMock()
        gl.projects.get.side_effect = RuntimeError("api down")

        enriched = enrich_include_release_metadata(
            {
                "include_type": "project",
                "project": "platform/ci-templates",
                "version": "1.0.0",
            },
            gitlab_url="https://gitlab.example.com",
            token="secret",
            gl=gl,
        )
        assert enriched["release_metadata_resolved"] is False

    def test_returns_early_when_no_semver_tags(self):
        project = MagicMock()
        project.tags.list.return_value = [_tag("main")]
        gl = MagicMock()
        gl.projects.get.return_value = project

        enriched = enrich_include_release_metadata(
            {
                "include_type": "project",
                "project": "platform/ci-templates",
                "version": "1.0.0",
            },
            gitlab_url="https://gitlab.example.com",
            token="secret",
            gl=gl,
        )
        assert enriched["release_metadata_resolved"] is False


class TestLoadYamlEntities:
    def test_include_entities_expose_valid_version(self, tmp_path):
        pipeline = tmp_path / ".gitlab-ci.yml"
        pipeline.write_text(
            "include:\n"
            "  - project: platform/ci-templates\n"
            "    ref: 1.2.0\n"
            "    file: security/gitleaks.yml\n"
            "job:\n"
            "  script:\n"
            "    - echo hi\n",
            encoding="utf-8",
        )

        entities, _unresolved = load_yaml_entities(str(pipeline))
        project_includes = [
            item for item in entities["includes"] if item["include_type"] == "project"
        ]
        assert project_includes
        assert project_includes[0]["valid_version"] is True
        assert project_includes[0]["version"] == "1.2.0"


class TestEnrichIncludesWithReleases:
    def test_batch_enrichment(self):
        includes = [
            {
                "include_type": "project",
                "project": "platform/ci-templates",
                "version": "1.0.0",
            }
        ]
        project = MagicMock()
        project.tags.list.return_value = [_tag("1.0.0")]
        gl = MagicMock()
        gl.projects.get.return_value = project

        with patch("gitlab.Gitlab", return_value=gl):
            enriched = enrich_includes_with_releases(
                includes,
                gitlab_url="https://gitlab.example.com",
                token="secret",
            )

        assert enriched[0]["release_metadata_resolved"] is True
        assert enriched[0]["update_available"] is False

    def test_shared_cache_reuses_gitlab_tag_fetch(self):
        includes = [
            {
                "include_type": "project",
                "project": "platform/ci-templates",
                "version": "1.0.0",
            },
            {
                "include_type": "project",
                "project": "platform/ci-templates",
                "version": "1.1.0",
            },
        ]
        project = MagicMock()
        project.tags.list.return_value = [
            _tag("1.0.0"),
            _tag("1.1.0"),
            _tag("1.2.0"),
        ]
        gl = MagicMock()
        gl.projects.get.return_value = project

        from src.compliance.release_cache import ReleaseMetadataCache

        cache = ReleaseMetadataCache()
        with patch(
            "src.compliance.include_versions._create_gitlab_client",
            return_value=gl,
        ) as create_client:
            enriched = enrich_includes_with_releases(
                includes,
                gitlab_url="https://gitlab.example.com",
                token="secret",
                cache=cache,
            )

        assert create_client.call_count == 1
        assert gl.projects.get.call_count == 1
        assert project.tags.list.call_count == 1
        assert enriched[0]["latest_version"] == "1.2.0"
        assert enriched[1]["latest_version"] == "1.2.0"

    def test_parallel_enrich_fetches_unique_projects_once(self):
        includes = [
            {
                "include_type": "project",
                "project": "platform/ci-templates",
                "version": "1.0.0",
            },
            {
                "include_type": "project",
                "project": "platform/other",
                "version": "2.0.0",
            },
            {
                "include_type": "project",
                "project": "platform/ci-templates",
                "version": "1.1.0",
            },
        ]

        def _project_for(path):
            project = MagicMock()
            if path == "platform/ci-templates":
                project.tags.list.return_value = [
                    _tag("1.0.0"),
                    _tag("1.1.0"),
                    _tag("1.2.0"),
                ]
            else:
                project.tags.list.return_value = [_tag("2.0.0"), _tag("2.1.0")]
            return project

        clients: list[MagicMock] = []

        def _new_client(_url, _token):
            gl = MagicMock()
            gl.projects.get.side_effect = _project_for
            clients.append(gl)
            return gl

        from src.compliance.release_cache import ReleaseMetadataCache

        cache = ReleaseMetadataCache()
        with patch(
            "src.compliance.include_versions._create_gitlab_client",
            side_effect=_new_client,
        ):
            enriched = enrich_includes_with_releases(
                includes,
                gitlab_url="https://gitlab.example.com",
                token="secret",
                cache=cache,
            )

        # One dedicated client per unique project (not a shared session).
        assert len(clients) == 2
        fetched_paths = sorted(
            call.args[0]
            for client in clients
            for call in client.projects.get.call_args_list
        )
        assert fetched_paths == ["platform/ci-templates", "platform/other"]
        assert enriched[0]["latest_version"] == "1.2.0"
        assert enriched[1]["latest_version"] == "2.1.0"
        assert enriched[2]["latest_version"] == "1.2.0"

    def test_parallel_prefetch_uses_dedicated_clients(self):
        includes = [
            {
                "include_type": "project",
                "project": "platform/one",
                "version": "1.0.0",
            },
            {
                "include_type": "project",
                "project": "platform/two",
                "version": "1.0.0",
            },
        ]
        client_ids: list[int] = []

        def _new_client(_url, _token):
            gl = MagicMock()
            project = MagicMock()
            project.tags.list.return_value = [_tag("1.0.0")]
            gl.projects.get.return_value = project
            client_ids.append(id(gl))
            return gl

        from src.compliance.release_cache import ReleaseMetadataCache

        with patch(
            "src.compliance.include_versions._create_gitlab_client",
            side_effect=_new_client,
        ):
            enrich_includes_with_releases(
                includes,
                gitlab_url="https://gitlab.example.com",
                token="secret",
                cache=ReleaseMetadataCache(),
            )

        assert len(client_ids) == 2
        assert len(set(client_ids)) == 2

    def test_fetch_semver_tag_dates_uses_cache(self):
        from src.compliance.release_cache import ReleaseMetadataCache

        cache = ReleaseMetadataCache()
        cached_dates = {"1.0.0": datetime(2024, 1, 1, tzinfo=timezone.utc)}
        cache.set_gitlab_tag_dates(
            "https://gitlab.example.com", "platform/ci-templates", cached_dates
        )
        gl = MagicMock()

        dates = fetch_semver_tag_dates(
            gl,
            "platform/ci-templates",
            gitlab_url="https://gitlab.example.com",
            cache=cache,
        )

        gl.projects.get.assert_not_called()
        assert dates == cached_dates
