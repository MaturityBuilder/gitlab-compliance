from pathlib import Path

from src.compliance.include_fix import (
    IncludeVersionFix,
    apply_include_version_fixes,
    collect_include_version_fixes,
)


class TestCollectIncludeVersionFixes:
    def test_collects_project_and_component_fixes(self):
        entities = {
            "includes": [
                {
                    "include_type": "project",
                    "project": "platform/ci-templates",
                    "version": "1.0.0",
                    "latest_version": "2.0.0",
                    "update_available": True,
                    "source_file": "ci.yml",
                    "line": 1,
                },
                {
                    "include_type": "local",
                    "version": "n/a",
                    "update_available": False,
                },
            ]
        }
        fixes = collect_include_version_fixes(entities)
        assert len(fixes) == 1
        assert fixes[0].latest_version == "2.0.0"


class TestApplyIncludeVersionFixes:
    def test_patches_project_ref(self, tmp_path):
        pipeline = tmp_path / ".gitlab-ci.yml"
        pipeline.write_text(
            "include:\n"
            "  - project: platform/ci-templates\n"
            "    ref: 1.0.0\n"
            "    file: security/gitleaks.yml\n",
            encoding="utf-8",
        )
        fixes = [
            IncludeVersionFix(
                source_file=str(pipeline),
                line=2,
                include_type="project",
                project="platform/ci-templates",
                current_version="1.0.0",
                latest_version="2.0.0",
            )
        ]
        applied = apply_include_version_fixes(fixes)
        assert applied
        assert "ref: 2.0.0" in pipeline.read_text(encoding="utf-8")
