"""Tests for external include fetching."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import requests

from src.compliance.include_fetch import (
    ExternalIncludeContext,
    FetchedInclude,
    IncludeFetchCache,
    IncludeFetchFailure,
    context_for_fetched,
    default_gitlab_url,
    fetch_include_content,
    include_reference_label,
    is_public_gitlab_host,
    remote_directory_url,
    remote_url_allows_token,
    resolve_nested_local_from_context,
)


class TestFetchRemoteInclude:
    def test_fetch_remote_public_url(self):
        parsed = {
            "include_type": "remote",
            "project": "https://example.com/ci.yml",
        }
        with patch("src.compliance.include_fetch.requests.get") as mock_get:
            mock_get.return_value = MagicMock(
                status_code=200,
                text="job:\n  script: [echo remote]\n",
            )
            mock_get.return_value.raise_for_status = MagicMock()
            result = fetch_include_content(
                parsed,
                gitlab_url="https://gitlab.com",
                token=None,
                cache=IncludeFetchCache(),
            )
        assert result.config_label == "https://example.com/ci.yml"
        assert "echo remote" in result.yaml_text

    def test_fetch_remote_uses_token_header(self):
        parsed = {
            "include_type": "remote",
            "project": "https://gitlab.com/group/project/-/raw/main/ci.yml",
        }
        with patch("src.compliance.include_fetch.requests.get") as mock_get:
            mock_get.return_value = MagicMock(
                status_code=200,
                text="job:\n  script: [echo]\n",
            )
            mock_get.return_value.raise_for_status = MagicMock()
            fetch_include_content(
                parsed,
                gitlab_url="https://gitlab.com",
                token="glpat-test",
                cache=IncludeFetchCache(),
            )
        headers = mock_get.call_args.kwargs["headers"]
        assert headers["PRIVATE-TOKEN"] == "glpat-test"

    def test_fetch_remote_omits_token_for_foreign_host(self):
        parsed = {
            "include_type": "remote",
            "project": "https://evil.example/private.yml",
        }
        with patch("src.compliance.include_fetch.requests.get") as mock_get:
            mock_get.return_value = MagicMock(
                status_code=200,
                text="job:\n  script: [echo]\n",
            )
            mock_get.return_value.raise_for_status = MagicMock()
            fetch_include_content(
                parsed,
                gitlab_url="https://gitlab.com",
                token="glpat-test",
                cache=IncludeFetchCache(),
            )
        headers = mock_get.call_args.kwargs["headers"]
        assert "PRIVATE-TOKEN" not in headers

    def test_fetch_remote_failure(self):
        parsed = {
            "include_type": "remote",
            "project": "https://example.com/missing.yml",
        }
        with patch("src.compliance.include_fetch.requests.get") as mock_get:
            mock_get.side_effect = requests.RequestException("404")
            result = fetch_include_content(
                parsed,
                gitlab_url="https://gitlab.com",
                token=None,
                cache=IncludeFetchCache(),
            )
        assert isinstance(result, IncludeFetchFailure)
        assert result.reason == "fetch_failed"

    def test_fetch_remote_empty_and_invalid_yaml(self):
        parsed = {
            "include_type": "remote",
            "project": "https://example.com/empty.yml",
        }
        with patch("src.compliance.include_fetch.requests.get") as mock_get:
            mock_get.return_value = MagicMock(status_code=200, text="   ")
            mock_get.return_value.raise_for_status = MagicMock()
            empty = fetch_include_content(
                parsed,
                gitlab_url="https://gitlab.com",
                token=None,
                cache=IncludeFetchCache(),
            )
        assert isinstance(empty, IncludeFetchFailure)
        assert "empty" in empty.detail

        with patch("src.compliance.include_fetch.requests.get") as mock_get:
            mock_get.return_value = MagicMock(status_code=200, text=":\n  - bad: [\n")
            mock_get.return_value.raise_for_status = MagicMock()
            invalid = fetch_include_content(
                {
                    "include_type": "remote",
                    "project": "https://example.com/bad.yml",
                },
                gitlab_url="https://gitlab.com",
                token=None,
                cache=IncludeFetchCache(),
            )
        assert isinstance(invalid, IncludeFetchFailure)
        assert "invalid YAML" in invalid.detail

    def test_fetch_remote_uses_cache(self):
        parsed = {
            "include_type": "remote",
            "project": "https://example.com/cached.yml",
        }
        cache = IncludeFetchCache()
        with patch("src.compliance.include_fetch.requests.get") as mock_get:
            mock_get.return_value = MagicMock(
                status_code=200,
                text="job:\n  script: [echo]\n",
            )
            mock_get.return_value.raise_for_status = MagicMock()
            first = fetch_include_content(
                parsed,
                gitlab_url="https://gitlab.com",
                token=None,
                cache=cache,
            )
            second = fetch_include_content(
                parsed,
                gitlab_url="https://gitlab.com",
                token=None,
                cache=cache,
            )
        assert first is second
        assert mock_get.call_count == 1


class TestFetchProjectInclude:
    def test_fetch_project_requires_token(self):
        parsed = {
            "include_type": "project",
            "project": "group/project",
            "version": "main",
            "file": ".gitlab-ci.yml",
        }
        result = fetch_include_content(
            parsed,
            gitlab_url="https://gitlab.com",
            token=None,
            cache=IncludeFetchCache(),
        )
        assert isinstance(result, IncludeFetchFailure)
        assert result.reason == "no_token"

    def test_fetch_project_file(self):
        parsed = {
            "include_type": "project",
            "project": "group/project",
            "version": "main",
            "file": "ci/child.yml",
        }
        mock_project = MagicMock()
        mock_project.files.raw.return_value = b"child:\n  script: [echo child]\n"
        mock_gl = MagicMock()
        mock_gl.projects.get.return_value = mock_project
        with patch("src.compliance.include_fetch._gitlab_client", return_value=mock_gl):
            result = fetch_include_content(
                parsed,
                gitlab_url="https://gitlab.com",
                token="glpat-test",
                cache=IncludeFetchCache(),
            )
        assert "echo child" in result.yaml_text
        mock_project.files.raw.assert_called_once_with(
            file_path="ci/child.yml", ref="main"
        )

    def test_fetch_project_default_file_and_list(self):
        mock_project = MagicMock()
        mock_project.files.raw.return_value = b"job:\n  script: [echo]\n"
        mock_gl = MagicMock()
        mock_gl.projects.get.return_value = mock_project
        with patch("src.compliance.include_fetch._gitlab_client", return_value=mock_gl):
            result = fetch_include_content(
                {
                    "include_type": "project",
                    "project": "group/project",
                    "version": "main",
                    "file": None,
                },
                gitlab_url="https://gitlab.com",
                token="glpat-test",
                cache=IncludeFetchCache(),
            )
            listed = fetch_include_content(
                {
                    "include_type": "project",
                    "project": "group/project",
                    "version": "main",
                    "file": ["a.yml", "b.yml"],
                },
                gitlab_url="https://gitlab.com",
                token="glpat-test",
                cache=IncludeFetchCache(),
            )
        assert isinstance(result, FetchedInclude)
        assert isinstance(listed, FetchedInclude)
        assert mock_project.files.raw.call_count == 3

    def test_fetch_project_file_errors(self):
        mock_project = MagicMock()
        mock_project.files.raw.side_effect = RuntimeError("missing")
        mock_gl = MagicMock()
        mock_gl.projects.get.return_value = mock_project
        with patch("src.compliance.include_fetch._gitlab_client", return_value=mock_gl):
            missing = fetch_include_content(
                {
                    "include_type": "project",
                    "project": "group/project",
                    "file": "gone.yml",
                },
                gitlab_url="https://gitlab.com",
                token="glpat-test",
                cache=IncludeFetchCache(),
            )
        assert isinstance(missing, IncludeFetchFailure)

        mock_project.files.raw.side_effect = None
        mock_project.files.raw.return_value = b":\n  [\n"
        with patch("src.compliance.include_fetch._gitlab_client", return_value=mock_gl):
            bad_yaml = fetch_include_content(
                {
                    "include_type": "project",
                    "project": "group/project",
                    "file": "bad.yml",
                },
                gitlab_url="https://gitlab.com",
                token="glpat-test",
                cache=IncludeFetchCache(),
            )
        assert isinstance(bad_yaml, IncludeFetchFailure)
        assert "invalid YAML" in bad_yaml.detail

    def test_fetch_project_unresolvable_path(self):
        with patch(
            "src.compliance.include_fetch.resolve_include_project_path",
            return_value=None,
        ):
            result = fetch_include_content(
                {"include_type": "project", "project": ""},
                gitlab_url="https://gitlab.com",
                token="glpat-test",
                cache=IncludeFetchCache(),
            )
        assert isinstance(result, IncludeFetchFailure)
        assert "could not resolve" in result.detail


class TestTemplateAndHelpers:
    def test_allow_template_fetches(self):
        with patch("src.compliance.include_fetch.requests.get") as mock_get:
            mock_get.return_value = MagicMock(
                status_code=200,
                text="job:\n  script: [echo template]\n",
            )
            mock_get.return_value.raise_for_status = MagicMock()
            cache = IncludeFetchCache()
            result = fetch_include_content(
                {"include_type": "template", "project": "Jobs/Build.gitlab-ci.yml"},
                gitlab_url="https://gitlab.com",
                token=None,
                cache=cache,
                allow_template=True,
            )
            again = fetch_include_content(
                {"include_type": "template", "project": "Jobs/Build.gitlab-ci.yml"},
                gitlab_url="https://gitlab.com",
                token=None,
                cache=cache,
                allow_template=True,
            )
        assert "echo template" in result.yaml_text
        assert again is result
        assert mock_get.call_count == 1

    def test_empty_template_name(self):
        result = fetch_include_content(
            {"include_type": "template", "project": "  "},
            gitlab_url="https://gitlab.com",
            token=None,
            allow_template=True,
        )
        assert isinstance(result, IncludeFetchFailure)
        assert result.reason == "unsupported_type"

    def test_unknown_include_type(self):
        result = fetch_include_content(
            {"include_type": "weird", "project": "x"},
            gitlab_url="https://gitlab.com",
            token=None,
        )
        assert isinstance(result, IncludeFetchFailure)
        assert result.detail == "weird"

    def test_context_for_fetched_variants(self):
        remote = context_for_fetched(
            {"include_type": "remote", "project": "https://example.com/ci/root.yml"},
            FetchedInclude("https://example.com/ci/root.yml", "x: 1\n"),
        )
        assert remote.kind == "remote"
        assert remote.base_url.endswith("/ci/")

        project = context_for_fetched(
            {
                "include_type": "project",
                "project": "group/project",
                "version": "v1",
            },
            FetchedInclude("project:group/project@v1:.gitlab-ci.yml", "x: 1\n"),
        )
        assert project.kind == "project"
        assert project.project_path == "group/project"
        assert project.ref == "v1"

        other = context_for_fetched(
            {"include_type": "component"},
            FetchedInclude("component:x", "x: 1\n"),
        )
        assert other.kind == "component"

    def test_resolve_nested_local_remote_and_project(self):
        cache = IncludeFetchCache()
        remote_ctx = ExternalIncludeContext(
            kind="remote",
            visit_key="https://example.com/ci/root.yml",
            base_url="https://example.com/ci/",
        )
        with patch("src.compliance.include_fetch.requests.get") as mock_get:
            mock_get.return_value = MagicMock(
                status_code=200,
                text="nested:\n  script: [echo]\n",
            )
            mock_get.return_value.raise_for_status = MagicMock()
            first = resolve_nested_local_from_context(
                "nested.yml",
                remote_ctx,
                gitlab_url="https://gitlab.com",
                token=None,
                cache=cache,
            )
            second = resolve_nested_local_from_context(
                "nested.yml",
                remote_ctx,
                gitlab_url="https://gitlab.com",
                token=None,
                cache=cache,
            )
        assert isinstance(first, FetchedInclude)
        assert first is second

        project_ctx = ExternalIncludeContext(
            kind="project",
            visit_key="project:group/p@main:a.yml",
            project_path="group/p",
            ref="main",
        )
        assert isinstance(
            resolve_nested_local_from_context(
                "child.yml",
                project_ctx,
                gitlab_url="https://gitlab.com",
                token=None,
                cache=IncludeFetchCache(),
            ),
            IncludeFetchFailure,
        )
        mock_project = MagicMock()
        mock_project.files.raw.return_value = b"job:\n  script: [echo]\n"
        mock_gl = MagicMock()
        mock_gl.projects.get.return_value = mock_project
        with patch("src.compliance.include_fetch._gitlab_client", return_value=mock_gl):
            fetched = resolve_nested_local_from_context(
                "child.yml",
                project_ctx,
                gitlab_url="https://gitlab.com",
                token="glpat-test",
                cache=IncludeFetchCache(),
            )
        assert isinstance(fetched, FetchedInclude)

        unsupported = resolve_nested_local_from_context(
            "x.yml",
            ExternalIncludeContext(kind="component", visit_key="c"),
            gitlab_url="https://gitlab.com",
            token=None,
            cache=IncludeFetchCache(),
        )
        assert unsupported.reason == "unsupported_type"

    def test_reference_labels_and_url_helpers(self, monkeypatch):
        assert (
            include_reference_label({"include_type": "local", "project": "ci.yml"})
            == "ci.yml"
        )
        assert include_reference_label(
            {
                "include_type": "project",
                "project": "g/p",
                "file": "a.yml",
                "version": "main",
            }
        ).startswith("g/p")
        assert (
            include_reference_label(
                {"include_type": "component", "project": "c", "version": "1"}
            )
            == "c@1"
        )
        assert (
            include_reference_label(
                {"include_type": "template", "project": "Jobs/Build.gitlab-ci.yml"}
            )
            == "Jobs/Build.gitlab-ci.yml"
        )
        assert include_reference_label({"include_type": "other", "project": "x"}) == "x"

        assert remote_directory_url("https://example.com/a/b.yml").endswith("/a/")
        assert remote_url_allows_token("https://gitlab.com/x", None) is False
        assert remote_url_allows_token("https://gitlab.com/x", "https://") is False
        assert remote_url_allows_token("https://www.gitlab.com/x", "https://gitlab.com")
        assert is_public_gitlab_host("https://gitlab.com/foo")
        assert not is_public_gitlab_host("https://example.com")

        assert default_gitlab_url("https://gitlab.example/") == "https://gitlab.example"
        monkeypatch.delenv("CI_SERVER_URL", raising=False)
        monkeypatch.setenv("GITLAB_URL", "https://self.gitlab/")
        assert default_gitlab_url() == "https://self.gitlab"
        monkeypatch.delenv("GITLAB_URL", raising=False)
        assert default_gitlab_url() == "https://gitlab.com"


class TestUnsupportedIncludes:
    @pytest.mark.parametrize("include_type", ["component", "template"])
    def test_component_and_template_unsupported_by_default(self, include_type):
        parsed = {
            "include_type": include_type,
            "project": "gitlab.com/org/component@1.0.0",
            "version": "1.0.0",
        }
        result = fetch_include_content(
            parsed,
            gitlab_url="https://gitlab.com",
            token="glpat-test",
            cache=IncludeFetchCache(),
        )
        assert isinstance(result, IncludeFetchFailure)
        assert result.reason == "unsupported_type"
