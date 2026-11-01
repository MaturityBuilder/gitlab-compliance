"""Tests for pipeline SBOM inventory and CycloneDX output."""

import json
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from src.compliance.image_versions import resolve_declared_image_digest
from src.compliance.include_fetch import (
    FetchedInclude,
    IncludeFetchFailure,
    resolve_project_commit_sha,
)
from src.compliance.sbom import (
    _add_component,
    build_purl,
    components_from_pipeline,
    load_pipeline_inventory,
    resolve_inventory,
)
from src.compliance.sbom_cyclonedx import (
    build_cyclonedx_sbom,
    render_cyclonedx_document,
)
from src.compliance.script_analysis import _package_record, extract_script_packages
from src.gitlab_compliance import gitlab_compliance
from src.modules.pipeline_data import collect_pipeline_data

PIPELINE = """
include:
  - local: ci/child.yml
  - project: platform/ci-templates
    ref: 1.2.3
    file: security/scan.yml
  - component: gitlab.com/org/pipeline@1.2.0
  - template: Auto-DevOps.gitlab-ci.yml
  - remote: https://gitlab.com/group/proj/-/raw/2.1.0/ci/template.yml

default:
  image: python:3.12.1

.base:
  image: golang:1.22.5
  before_script:
    - apk add curl=8.5.0-r0

build:
  extends: .base
  services:
    - docker:24.0.5-dind
  script:
    - pip install requests==2.31.0
    - pip install flask
    - npm install -g lodash@4.17.21
    - go install golang.org/x/tools/cmd/goimports@v0.16.0
    - apt-get install wget=1.21.4-1
    - dnf install curl-7.76.1-23.el9
    - docker pull alpine:3.20

plain:
  script:
    - echo only
"""


def _write_pipeline(tmp_path):
    child_dir = tmp_path / "ci"
    child_dir.mkdir()
    (child_dir / "child.yml").write_text(
        "child:\n  script: [echo child]\n",
        encoding="utf-8",
    )
    pipeline = tmp_path / ".gitlab-ci.yml"
    pipeline.write_text(PIPELINE, encoding="utf-8")
    return pipeline


def _document(tmp_path, **kwargs):
    pipeline = _write_pipeline(tmp_path)
    text = build_cyclonedx_sbom(
        str(pipeline),
        serial_number="urn:uuid:00000000-0000-0000-0000-000000000001",
        timestamp="2026-01-01T00:00:00Z",
        **kwargs,
    )
    return pipeline, json.loads(text)


class TestScriptPackageExtraction:
    def test_extracts_pinned_and_unpinned_packages(self):
        job = {
            "name": "build",
            "source_file": "ci.yml",
            "line": 4,
            "script": [
                "pip install requests==2.31.0 'pkg[extra]==1.0' flask>=1",
                "pip install requests[security]@git+https://github.com/psf/requests.git",
                "apk add curl=8.5.0-r0 busybox",
                "npm install -g @scope/pkg@1.2.3 lodash",
                "go install example.com/tool example.com/float@latest example.com/other@v0.1.0 -ldflags=-s",
                "yum install /tmp/curl.rpm",
                "docker run --rm -v /data:/data alpine:3.20",
            ],
        }
        found = {
            (item["ecosystem"], item["name"], item["version"], item["pinned"])
            for item in extract_script_packages(job)
        }
        assert ("pypi", "requests", "2.31.0", True) in found
        assert (
            "pypi",
            "requests",
            "git+https://github.com/psf/requests.git",
            True,
        ) in found
        assert ("pypi", "pkg", "1.0", True) in found
        assert ("pypi", "flask", "", False) in found
        assert ("apk", "curl", "8.5.0-r0", True) in found
        assert ("apk", "busybox", "", False) in found
        assert ("npm", "@scope/pkg", "1.2.3", True) in found
        assert ("npm", "lodash", "", False) in found
        assert ("golang", "example.com/tool", "", False) in found
        assert ("golang", "example.com/other", "v0.1.0", True) in found
        assert ("rpm", "curl.rpm", "", True) in found
        assert ("docker", "alpine:3.20", "", True) in found

    def test_uses_script_provenance_locations(self):
        job = {
            "name": "build",
            "source_file": "root.yml",
            "line": 1,
            "script_provenance": [
                {
                    "text": "pip install requests==2.31.0",
                    "source_file": "template.yml",
                    "source_line": 9,
                },
                {"text": "", "source_file": "template.yml", "source_line": 10},
            ],
            "script": ["pip install should-not-appear==1"],
        }
        packages = extract_script_packages(job)
        assert len(packages) == 1
        assert packages[0]["source_file"] == "template.yml"
        assert packages[0]["line"] == 9
        assert packages[0]["parent_job"] == "build"
        assert _package_record("pypi", "-r", "", False) is None


class TestEffectiveInventory:
    def test_pipeline_inventory_covers_includes_images_and_packages(self, tmp_path):
        pipeline, document = _document(tmp_path, project="group/app")
        purls = {item["purl"] for item in document["components"]}
        assert any(purl.startswith("pkg:oci/library/python@3.12.1") for purl in purls)
        assert any("golang" in purl and "1.22.5" in purl for purl in purls)
        assert any(
            purl.startswith("pkg:oci/library/docker@24.0.5-dind") for purl in purls
        )
        assert any(purl.startswith("pkg:oci/library/alpine@3.20") for purl in purls)
        assert "pkg:pypi/requests@2.31.0" in purls
        assert "pkg:pypi/flask" in purls
        assert "pkg:apk/curl@8.5.0-r0" in purls
        assert "pkg:npm/lodash@4.17.21" in purls
        assert "pkg:golang/golang.org/x/tools/cmd/goimports@v0.16.0" in purls
        assert "pkg:deb/wget@1.21.4-1" in purls
        assert any(purl.startswith("pkg:rpm/curl@7.76.1") for purl in purls)
        assert any(
            purl.startswith("pkg:gitlab/platform/ci-templates@1.2.3") for purl in purls
        )
        assert any("component=pipeline" in purl for purl in purls)
        assert any(purl.startswith("pkg:generic/gitlab-template/") for purl in purls)
        assert any("template.yml" in purl and "@2.1.0" in purl for purl in purls)
        assert any(item["name"] == "child.yml" for item in document["components"])

        golang = next(
            item for item in document["components"] if item["name"] == "golang"
        )
        assert golang["properties"]
        sources = {prop["value"] for prop in golang["properties"]}
        assert "extends" in sources
        assert len(golang["evidence"]["occurrences"]) == 1

        python = next(
            item for item in document["components"] if item["name"] == "python"
        )
        jobs = {item["additionalContext"] for item in python["evidence"]["occurrences"]}
        assert "plain" in jobs
        assert "child" in jobs
        assert "build" not in jobs
        assert (
            document["metadata"]["component"]["properties"][0]["value"] == "group/app"
        )
        assert (
            document["metadata"]["tools"]["components"][0]["name"]
            == "gitlab-compliance"
        )
        assert document["dependencies"][0]["ref"] == "pipeline"
        assert os_path_basename_in_metadata(document, pipeline)

    def test_duplicate_images_collapse_to_one_component(self, tmp_path):
        pipeline = tmp_path / ".gitlab-ci.yml"
        pipeline.write_text(
            "one:\n  image: alpine:3.20\n  script: [echo]\n"
            "two:\n  image: alpine:3.20\n  script: [echo]\n",
            encoding="utf-8",
        )
        data = collect_pipeline_data(
            str(pipeline),
            resolve_job_composition=True,
        )
        components = components_from_pipeline(data, str(pipeline))
        alpine = [item for item in components if item["name"] == "alpine"]
        assert len(alpine) == 1
        assert len(alpine[0]["occurrences"]) == 2


def os_path_basename_in_metadata(document, pipeline):
    return document["metadata"]["component"]["name"] == pipeline.name


class TestDeclaredDigestResolution:
    def test_uses_declared_tag_digest_not_latest_tag(self):
        with (
            patch(
                "src.compliance.image_versions._fetch_docker_hub_digest",
                return_value="abc123",
            ) as fetch_digest,
            patch(
                "src.compliance.image_versions._list_docker_hub_tags",
            ) as list_tags,
        ):
            digest = resolve_declared_image_digest("library/python:1.2.3")
        assert digest == "abc123"
        fetch_digest.assert_called_once()
        assert fetch_digest.call_args.args[1] == "1.2.3"
        list_tags.assert_not_called()

    def test_returns_digest_already_written_in_the_reference(self):
        digest = "a" * 64
        assert resolve_declared_image_digest(f"alpine@sha256:{digest}") == digest

    def test_gitlab_registry_uses_declared_tag(self):
        with patch(
            "src.compliance.image_versions._fetch_gitlab_registry_digest",
            return_value="def456",
        ) as fetch_digest:
            digest = resolve_declared_image_digest(
                "registry.gitlab.example/group/app:1.0.0",
                gitlab_url="https://gitlab.example",
                token="token",
            )
        assert digest == "def456"
        assert fetch_digest.call_args.args[1] == "1.0.0"

    def test_unsupported_registry_and_errors_stay_unresolved(self):
        assert resolve_declared_image_digest("ghcr.io/org/app:1.2.3") == ""
        with patch(
            "src.compliance.image_versions._fetch_docker_hub_digest",
            side_effect=RuntimeError("down"),
        ):
            assert resolve_declared_image_digest("python:3.12") == ""
        assert resolve_declared_image_digest("") == ""
        assert resolve_declared_image_digest(":") == ""


class TestResolveInventory:
    def test_project_commit_and_file_hashes_do_not_replace_declared_version(
        self, tmp_path
    ):
        pipeline = _write_pipeline(tmp_path)
        data = collect_pipeline_data(str(pipeline), resolve_job_composition=True)

        def fake_digest(image_ref, **kwargs):
            if image_ref.startswith("python:"):
                return "111"
            return ""

        with (
            patch(
                "src.compliance.sbom.resolve_declared_image_digest",
                side_effect=fake_digest,
            ),
            patch(
                "src.compliance.sbom.resolve_project_commit_sha",
                return_value="c" * 40,
            ),
            patch(
                "src.compliance.sbom.fetch_include_content",
                return_value=FetchedInclude(
                    config_label="remote", yaml_text="job: {}\n"
                ),
            ),
        ):
            resolved = resolve_inventory(
                data,
                pipeline_file=str(pipeline),
                gitlab_url="https://gitlab.com",
                token="token",
            )

        project = next(
            item for item in resolved["includes"] if item["include_type"] == "project"
        )
        assert project["version"] == "1.2.3"
        assert project["resolved_commit"] == "c" * 40
        assert project["content_sha256"]
        local = next(
            item for item in resolved["includes"] if item["include_type"] == "local"
        )
        assert local["content_sha256"]
        component = next(
            item
            for item in components_from_pipeline(resolved, str(pipeline))
            if item["name"] == "python"
        )
        assert component["version"] == "3.12.1"
        assert component["properties"]["gitlab-compliance:resolved-digest"] == "111"
        assert component["hashes"] == ["111"]
        declared = component["properties"]["gitlab-compliance:declared-version"]
        assert declared == "3.12.1"

    def test_resolve_failures_leave_components_without_hashes(self, tmp_path):
        pipeline = _write_pipeline(tmp_path)
        data = collect_pipeline_data(str(pipeline), resolve_external_includes=False)
        with (
            patch(
                "src.compliance.sbom.resolve_declared_image_digest",
                return_value="",
            ),
            patch(
                "src.compliance.sbom.fetch_include_content",
                return_value=IncludeFetchFailure(reason="fetch_failed"),
            ),
            patch(
                "src.compliance.sbom.resolve_project_commit_sha",
                return_value="",
            ),
            patch(
                "src.compliance.sbom._sha256_file",
                side_effect=OSError("unreadable"),
            ),
        ):
            resolved = resolve_inventory(
                data,
                pipeline_file=str(pipeline),
                gitlab_url="https://gitlab.com",
                token="token",
            )
        local = next(
            item for item in resolved["includes"] if item["include_type"] == "local"
        )
        assert local.get("content_sha256") == ""
        remote = next(
            item for item in resolved["includes"] if item["include_type"] == "remote"
        )
        assert "content_sha256" not in remote

    def test_commit_lookup_returns_empty_without_a_token(self):
        assert (
            resolve_project_commit_sha(
                "group/app",
                "main",
                gitlab_url="https://gitlab.com",
                token="",
            )
            == ""
        )

    def test_commit_lookup_swallows_api_errors(self):
        with patch(
            "src.compliance.include_fetch._gitlab_client",
            side_effect=RuntimeError("nope"),
        ):
            assert (
                resolve_project_commit_sha(
                    "group/app",
                    "main",
                    gitlab_url="https://gitlab.com",
                    token="token",
                )
                == ""
            )

    def test_commit_lookup_reads_commit_id(self):
        commit = MagicMock()
        commit.id = "abc"
        project = MagicMock()
        project.commits.get.return_value = commit
        client = MagicMock()
        client.projects.get.return_value = project
        with patch(
            "src.compliance.include_fetch._gitlab_client",
            return_value=client,
        ):
            assert (
                resolve_project_commit_sha(
                    "group/app",
                    "1.2.3",
                    gitlab_url="https://gitlab.com",
                    token="token",
                )
                == "abc"
            )
        project.commits.get.assert_called_once_with("1.2.3")


class TestComponentEdges:
    def test_dedupes_templates_and_skips_unknown_rows(self):
        assert build_purl("oci", "library/alpine", "n/a", {"tag": "", "x": "1"}) == (
            "pkg:oci/library/alpine?x=1"
        )
        bucket: dict = {}
        _add_component(bucket, {"purl": ""})
        assert bucket == {}

        data = {
            "includes": [
                {
                    "include_type": "project",
                    "project": "group/app",
                    "version": "1.0.0",
                    "file": ["a.yml", "", "b.yml"],
                    "source_file": "ci.yml",
                    "line": 2,
                },
                {"include_type": "mystery", "project": "nope"},
                {
                    "include_type": "template",
                    "project": "Jobs/Build.gitlab-ci.yml",
                    "version": "",
                    "source_file": "ci.yml",
                    "line": 4,
                },
                {
                    "include_type": "template",
                    "project": "Jobs/Build.gitlab-ci.yml",
                    "version": "1.0.0",
                    "source_file": "ci.yml",
                    "line": 4,
                    "content_sha256": "abc",
                    "resolved_commit": "def",
                },
                {
                    "include_type": "remote",
                    "project": "https://example.com",
                    "version": "",
                    "source_file": "ci.yml",
                    "line": 5,
                },
                {
                    "include_type": "artifact",
                    "artifact": "",
                    "project": "",
                    "content_sha256": "fff",
                    "source_file": "ci.yml",
                    "line": 6,
                },
            ],
            "container_images": [{"image": "", "parent_job": "build"}],
            "script_packages": [
                {"ecosystem": "cargo", "name": "serde", "version": "1"},
                {
                    "ecosystem": "docker",
                    "name": "alpine:3.20",
                    "parent_job": "build",
                    "source_file": "ci.yml",
                    "line": 8,
                    "resolved_digest": "123",
                },
            ],
            "dynamic_child_pipelines": [
                {"include_type": "pipeline", "artifact": "skip.yml"},
                {
                    "include_type": "artifact",
                    "artifact": "generated.yml",
                    "source_file": "ci.yml",
                    "line": 9,
                    "content_sha256": "abc",
                },
            ],
        }
        components = components_from_pipeline(data, "ci.yml")
        by_name = {item["name"]: item for item in components}
        project = next(item for item in components if item["name"] == "app")
        assert "file=a.yml%2Cb.yml" in project["purl"]
        template = by_name["Jobs/Build.gitlab-ci.yml"]
        assert template["hashes"] == ["abc"]
        assert template["properties"]["gitlab-compliance:declared-version"] == "1.0.0"
        assert template["properties"]["gitlab-compliance:resolved-commit"] == "def"
        assert len(template["occurrences"]) == 1
        assert by_name["remote-include"]["external_references"][0]["url"] == (
            "https://example.com"
        )
        generated = next(
            item
            for item in components
            if item["purl"].startswith("pkg:generic/generated-pipeline")
        )
        assert generated["name"] == "include"
        assert generated["hashes"] == ["fff"]
        assert by_name["generated.yml"]["hashes"] == ["abc"]
        alpine = by_name["alpine"]
        assert alpine["properties"]["gitlab-compliance:resolved-digest"] == "123"
        assert "serde" not in by_name

    def test_cyclonedx_drops_empty_hashes_and_occurrences(self):
        document = render_cyclonedx_document(
            [
                {
                    "type": "library",
                    "name": "requests",
                    "version": "1",
                    "purl": "pkg:pypi/requests@1",
                    "hashes": ["", "ab"],
                    "properties": {"keep": "yes", "drop": ""},
                    "external_references": [],
                    "occurrences": [{"location": "", "line": 0, "context": ""}],
                }
            ],
            pipeline_file=".gitlab-ci.yml",
            serial_number="urn:uuid:00000000-0000-0000-0000-000000000002",
            timestamp="2026-01-01T00:00:00Z",
        )
        component = document["components"][0]
        assert component["hashes"] == [{"alg": "SHA-256", "content": "ab"}]
        assert "evidence" not in component
        assert component["properties"] == [{"name": "keep", "value": "yes"}]

    def test_resolve_artifact_files_and_unversioned_project_ref(self, tmp_path):
        pipeline = tmp_path / ".gitlab-ci.yml"
        pipeline.write_text("job:\n  script: [echo]\n", encoding="utf-8")
        generated = tmp_path / "generated.yml"
        generated.write_text("child:\n  script: [echo]\n", encoding="utf-8")
        data = {
            "container_images": [],
            "includes": [
                {
                    "include_type": "project",
                    "project": "group/app",
                    "version": "n/a",
                    "source_file": str(pipeline),
                    "line": 1,
                },
                {
                    "include_type": "project",
                    "project": "",
                    "version": "",
                    "source_file": str(pipeline),
                    "line": 2,
                },
            ],
            "script_packages": [],
            "dynamic_child_pipelines": [
                {"include_type": "pipeline", "artifact": "skip.yml"},
                {
                    "include_type": "artifact",
                    "artifact": "generated.yml",
                    "source_file": str(pipeline),
                    "line": 3,
                },
                {
                    "include_type": "artifact",
                    "artifact": "missing-generated.yml",
                    "source_file": str(pipeline),
                    "line": 4,
                },
            ],
        }
        with (
            patch(
                "src.compliance.sbom.resolve_declared_image_digest",
                return_value="",
            ),
            patch(
                "src.compliance.sbom.resolve_project_commit_sha",
                return_value="c" * 40,
            ) as commit,
            patch(
                "src.compliance.sbom.fetch_include_content",
                return_value=IncludeFetchFailure(reason="fetch_failed"),
            ),
        ):
            resolved = resolve_inventory(
                data,
                pipeline_file=str(pipeline),
                gitlab_url="https://gitlab.com",
                token="token",
            )
        commit.assert_called_once()
        assert commit.call_args.args[1] == "HEAD"
        children = {
            item.get("artifact"): item for item in resolved["dynamic_child_pipelines"]
        }
        assert children["generated.yml"]["content_sha256"]
        assert "content_sha256" not in children["missing-generated.yml"]
        assert children["skip.yml"]["include_type"] == "pipeline"

        with patch(
            "src.compliance.sbom._sha256_file",
            side_effect=OSError("unreadable"),
        ):
            failed = resolve_inventory(
                data,
                pipeline_file=str(pipeline),
                gitlab_url="https://gitlab.com",
                token=None,
            )
        failed_generated = next(
            item
            for item in failed["dynamic_child_pipelines"]
            if item.get("artifact") == "generated.yml"
        )
        assert failed_generated["content_sha256"] == ""

    def test_load_pipeline_inventory_can_resolve(self, tmp_path):
        pipeline = tmp_path / ".gitlab-ci.yml"
        pipeline.write_text(
            "job:\n  image: alpine:3.20\n  script: [echo]\n",
            encoding="utf-8",
        )
        with patch(
            "src.compliance.sbom.resolve_declared_image_digest",
            return_value="abc",
        ):
            data = load_pipeline_inventory(
                str(pipeline),
                include_nested=False,
                resolve=True,
            )
        assert data["container_images"][0]["resolved_digest"] == "abc"


class TestSbomCommand:
    def test_writes_cyclonedx_file_and_stdout(self, tmp_path):
        pipeline = _write_pipeline(tmp_path)
        output = tmp_path / "gl-sbom.cdx.json"
        runner = CliRunner()
        written = runner.invoke(
            gitlab_compliance,
            ["sbom", "-p", str(pipeline), "-o", str(output), "--project", "group/app"],
        )
        assert written.exit_code == 0, written.output
        document = json.loads(output.read_text(encoding="utf-8"))
        assert document["bomFormat"] == "CycloneDX"
        assert document["specVersion"] == "1.6"

        echoed = runner.invoke(gitlab_compliance, ["sbom", "-p", str(pipeline)])
        assert echoed.exit_code == 0, echoed.output
        assert json.loads(echoed.output)["bomFormat"] == "CycloneDX"

    def test_missing_pipeline_exits_2(self, tmp_path):
        result = CliRunner().invoke(
            gitlab_compliance,
            ["sbom", "-p", str(tmp_path / "missing.yml")],
        )
        assert result.exit_code == 2

    def test_invalid_yaml_exits_2(self, tmp_path):
        pipeline = tmp_path / ".gitlab-ci.yml"
        pipeline.write_text(":\n  - [\n", encoding="utf-8")
        result = CliRunner().invoke(
            gitlab_compliance,
            ["sbom", "-p", str(pipeline)],
        )
        assert result.exit_code == 2

    def test_unwritable_output_exits_2(self, tmp_path):
        pipeline = _write_pipeline(tmp_path)
        output_dir = tmp_path / "not-a-file"
        output_dir.mkdir()
        result = CliRunner().invoke(
            gitlab_compliance,
            ["sbom", "-p", str(pipeline), "-o", str(output_dir)],
        )
        assert result.exit_code == 2


@pytest.mark.parametrize(
    ("image_ref", "expected_tag"),
    [
        ("python:3.12.1", "3.12.1"),
        ("alpine@sha256:" + ("b" * 64), ""),
        ("alpine", "latest"),
        ("", ""),
    ],
)
def test_declared_image_tag(image_ref, expected_tag):
    from src.compliance.image_versions import declared_image_tag

    assert declared_image_tag(image_ref) == expected_tag
