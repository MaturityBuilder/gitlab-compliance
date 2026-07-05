from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from src.modules.release import (
    build_markdown,
    classify_commit,
    filter_commits_since_tag,
    generate_markdown,
    get_commits_since_last_tag,
    resolve_baseline_tag,
    sort_tags,
    summarize_commits,
)


def _tag(name: str, committed_date: str, commit_id: str):
    return SimpleNamespace(
        name=name,
        commit={"committed_date": committed_date, "id": commit_id},
    )


def _commit(title: str, commit_id: str, short_id: str | None = None, **kwargs):
    return SimpleNamespace(
        title=title,
        id=commit_id,
        short_id=short_id or commit_id[:8],
        author_name=kwargs.get("author_name"),
        web_url=kwargs.get("web_url"),
    )


class TestClassifyCommit:
    def test_conventional_prefixes(self):
        assert classify_commit("feat: add release notes") == "feat"
        assert classify_commit("fix(scope): handle auth") == "fix"
        assert classify_commit("chore: bump deps") == "chore"
        assert classify_commit("docs: update readme") == "other"
        assert classify_commit("refactor!: rewrite module") == "other"
        assert classify_commit("random commit") == "other"


class TestResolveBaselineTag:
    def test_no_tags(self):
        name, date, sha = resolve_baseline_tag([])
        assert name == "No previous tag"
        assert sha is None
        assert date.timestamp() == 0

    def test_explicit_since_tag(self):
        tags = [
            _tag("v1.0.0", "2024-01-01T00:00:00Z", "aaa"),
            _tag("v2.0.0", "2024-06-01T00:00:00Z", "bbb"),
        ]
        name, _, sha = resolve_baseline_tag(tags, since_tag="v1.0.0")
        assert name == "v1.0.0"
        assert sha == "aaa"

    def test_missing_since_tag_raises(self):
        with pytest.raises(ValueError, match="Tag 'missing' not found"):
            resolve_baseline_tag([], since_tag="missing")

    def test_latest_semver_tag_selected(self):
        tags = [
            _tag("v1.0.0", "2024-01-01T00:00:00Z", "aaa"),
            _tag("v2.1.0", "2024-03-01T00:00:00Z", "bbb"),
            _tag("v2.0.0", "2024-02-01T00:00:00Z", "ccc"),
        ]
        ordered = sort_tags(tags)
        name, _, sha = resolve_baseline_tag(ordered)
        assert name == "v2.1.0"
        assert sha == "bbb"


class TestFilterCommitsSinceTag:
    def test_excludes_tag_commit(self):
        commits = [
            _commit("tag commit", "tagsha123"),
            _commit("feat: new work", "newsha456"),
        ]
        filtered = filter_commits_since_tag(commits, "tagsha123")
        assert len(filtered) == 1
        assert filtered[0].id == "newsha456"


class TestSummarizeCommits:
    def test_bucket_counts(self):
        commits = [
            _commit("feat: one", "1"),
            _commit("fix: two", "2"),
            _commit("chore: three", "3"),
            _commit("docs: four", "4"),
        ]
        summary = summarize_commits(commits)
        assert summary == {"feat": 1, "fix": 1, "chore": 1, "other": 1}


class TestBuildMarkdown:
    def test_grouped_sections_and_links(self):
        commits = [
            _commit(
                "feat: add OCI",
                "111",
                web_url="https://gitlab.com/group/proj/-/commit/111",
                author_name="Alice",
            ),
            _commit("fix: line refs", "222"),
        ]
        summary = summarize_commits(commits)
        markdown = build_markdown(
            "group/project",
            "v1.0.6",
            datetime(2024, 6, 1, tzinfo=timezone.utc),
            commits,
            summary,
            project_web_url="https://gitlab.com/group/project",
        )
        assert "# Release Notes — group/project" in markdown
        assert "**Since tag:** v1.0.6 (2024-06-01)" in markdown
        assert "## Features" in markdown
        assert "## Fixes" in markdown
        assert "[feat: add OCI](https://gitlab.com/group/proj/-/commit/111)" in markdown
        assert "Alice" in markdown


class TestGenerateMarkdown:
    def test_creates_output_directory(self, tmp_path):
        output_dir = tmp_path / "nested" / "release-notes"
        commits = [_commit("feat: one", "1")]
        summary = summarize_commits(commits)
        path = generate_markdown(
            "group/project",
            "v1.0.0",
            datetime(2024, 1, 1, tzinfo=timezone.utc),
            commits,
            summary,
            output_dir,
        )
        assert path.exists()
        assert output_dir.exists()
        assert "release_notes_group_project_since_v1.0.0.md" == path.name


class TestGetCommitsSinceLastTag:
    def test_fetches_and_filters_commits(self):
        project = MagicMock()
        project.web_url = "https://gitlab.com/group/project"
        project.tags.list.return_value = [
            _tag("v1.0.0", "2024-01-01T00:00:00Z", "tagsha"),
        ]
        project.commits.list.return_value = [
            _commit("tag commit", "tagsha"),
            _commit("feat: new", "newsha"),
        ]

        gl = MagicMock()
        gl.projects.get.return_value = project

        returned_project, tag_name, _, commits = get_commits_since_last_tag(
            gl, "group/project"
        )
        assert returned_project is project
        assert tag_name == "v1.0.0"
        assert len(commits) == 1
        assert commits[0].id == "newsha"
        project.commits.list.assert_called_once()


class TestReleaseNotesCli:
    def _mock_gitlab(self):
        project = MagicMock()
        project.web_url = "https://gitlab.com/group/project"
        project.tags.list.return_value = [
            _tag("v1.0.0", "2024-01-01T00:00:00Z", "tagsha"),
        ]
        project.commits.list.return_value = [_commit("feat: add tests", "newsha")]

        gl = MagicMock()
        gl.projects.get.return_value = project
        return gl

    def test_success_without_ai_summary(self, tmp_path):
        runner = CliRunner()
        with patch("src.modules.release.gitlab.Gitlab", return_value=self._mock_gitlab()):
            result = runner.invoke(
                __import__("src.modules.release", fromlist=["release_notes"]).release_notes,
                [
                    "--token",
                    "test-token",
                    "--projects",
                    "group/project",
                    "--markdown",
                    str(tmp_path),
                    "--no-write",
                ],
            )
        assert result.exit_code == 0, result.output
        assert "Summary across all projects" in result.output
        assert "changelog.md" not in result.output

    def test_honors_markdown_directory(self, tmp_path):
        runner = CliRunner()
        markdown_dir = tmp_path / "notes"
        with patch("src.modules.release.gitlab.Gitlab", return_value=self._mock_gitlab()):
            result = runner.invoke(
                __import__("src.modules.release", fromlist=["release_notes"]).release_notes,
                [
                    "--token",
                    "test-token",
                    "--projects",
                    "group/project",
                    "--markdown",
                    str(markdown_dir),
                ],
            )
        assert result.exit_code == 0, result.output
        files = list(markdown_dir.glob("release_notes_*.md"))
        assert len(files) == 1

    def test_failure_exits_nonzero(self):
        runner = CliRunner()
        gl = MagicMock()
        gl.projects.get.side_effect = RuntimeError("project not found")
        with patch("src.modules.release.gitlab.Gitlab", return_value=gl):
            result = runner.invoke(
                __import__("src.modules.release", fromlist=["release_notes"]).release_notes,
                ["--token", "test-token", "--projects", "missing/project"],
            )
        assert result.exit_code == 1
        assert "Error processing missing/project" in result.output

    def test_no_successful_projects_exits_nonzero(self):
        runner = CliRunner()
        gl = MagicMock()
        gl.projects.get.side_effect = RuntimeError("boom")
        with patch("src.modules.release.gitlab.Gitlab", return_value=gl):
            result = runner.invoke(
                __import__("src.modules.release", fromlist=["release_notes"]).release_notes,
                [
                    "--token",
                    "test-token",
                    "--projects",
                    "a/b",
                    "--projects",
                    "c/d",
                ],
            )
        assert result.exit_code == 1
        assert "No projects processed successfully" in result.output
