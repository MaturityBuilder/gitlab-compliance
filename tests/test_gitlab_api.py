from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from src.compliance.gitlab_api import load_api_entities


class TestLoadApiEntities:
    def test_requires_token(self, monkeypatch):
        monkeypatch.delenv("GITLAB_TOKEN", raising=False)
        monkeypatch.delenv("CI_JOB_TOKEN", raising=False)
        with pytest.raises(ValueError, match="GitLab API token required"):
            load_api_entities(token=None)

    def test_loads_project_settings_and_variables(self):
        variable = SimpleNamespace(key="FOO", protected=True, masked=False)
        project = MagicMock()
        project.public_jobs = True
        project.variables.list.return_value = [variable]
        for key in (
            "auto_devops_enabled",
            "builds_access_level",
            "forking_access_level",
            "merge_requests_enabled",
            "jobs_enabled",
        ):
            setattr(project, key, "enabled")

        group = MagicMock()
        group.shared_runners_enabled = True
        group.request_access_enabled = False

        gl = MagicMock()
        gl.projects.get.return_value = project
        gl.groups.get.return_value = group

        with patch("gitlab.Gitlab", return_value=gl):
            entities = load_api_entities(
                gitlab_url="https://gitlab.example.com",
                token="secret",
                project="group/project",
                group="my-group",
            )

        assert entities["project_settings"]
        assert entities["project_ci_variables"][0]["name"] == "FOO"
        assert entities["group_settings"]

    def test_load_without_project_or_group(self):
        with patch("gitlab.Gitlab") as gitlab_cls:
            gl = MagicMock()
            gitlab_cls.return_value = gl
            entities = load_api_entities(
                token="secret", gitlab_url="https://gitlab.example.com"
            )
        assert entities["project_settings"] == []
