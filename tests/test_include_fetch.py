"""Tests for external include fetching."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import requests

from src.compliance.include_fetch import (
    IncludeFetchCache,
    IncludeFetchFailure,
    fetch_include_content,
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
            "project": "https://example.com/private.yml",
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
