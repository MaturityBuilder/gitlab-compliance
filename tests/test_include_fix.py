from pathlib import Path

from src.compliance.include_fix import (
    IncludeVersionFix,
    _apply_fix_to_file,
    _replace_component_line,
    _replace_ref_line,
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

    def test_skips_when_already_latest_or_not_updatable(self):
        entities = {
            "includes": [
                {
                    "include_type": "project",
                    "project": "platform/ci-templates",
                    "version": "2.0.0",
                    "latest_version": "2.0.0",
                    "update_available": True,
                },
                {
                    "include_type": "component",
                    "project": "gitlab.com/org/pipeline",
                    "version": "1.0.0",
                    "latest_version": "2.0.0",
                    "update_available": False,
                },
            ]
        }
        assert collect_include_version_fixes(entities) == []

    def test_collects_component_include_fix(self):
        entities = {
            "includes": [
                {
                    "include_type": "component",
                    "project": "gitlab.com/org/pipeline",
                    "version": "1.0.0",
                    "latest_version": "2.0.0",
                    "update_available": True,
                    "source_file": "ci.yml",
                    "line": 1,
                }
            ]
        }
        fixes = collect_include_version_fixes(entities)
        assert len(fixes) == 1
        assert fixes[0].include_type == "component"


class TestIncludeFixHelpers:
    def test_replace_ref_line_with_quotes(self):
        updated = _replace_ref_line('  ref: "1.0.0"\n', "2.0.0")
        assert updated == '  ref: "2.0.0"\n'

    def test_replace_component_line(self):
        line = "  - component: gitlab.com/org/pipeline@1.0.0\n"
        updated = _replace_component_line(line, "1.0.0", "2.0.0")
        assert updated == "  - component: gitlab.com/org/pipeline@2.0.0\n"

    def test_replace_component_line_with_spaced_key(self):
        line = "  - component : gitlab.com/org/pipeline@1.0.0\n"
        updated = _replace_component_line(line, "1.0.0", "2.0.0")
        assert "2.0.0" in updated

    def test_replace_component_line_returns_none_for_non_component(self):
        assert _replace_component_line("  ref: 1.0.0\n", "1.0.0", "2.0.0") is None

    def test_replace_component_line_returns_none_when_version_missing(self):
        line = "  - component: gitlab.com/org/pipeline@9.9.9\n"
        assert _replace_component_line(line, "1.0.0", "2.0.0") is None

    def test_apply_fix_rejects_invalid_line_and_include_block(self, tmp_path):
        pipeline = tmp_path / ".gitlab-ci.yml"
        pipeline.write_text(
            "include:\n  - project: platform/ci-templates\n",
            encoding="utf-8",
        )
        invalid_line = IncludeVersionFix(
            source_file=str(pipeline),
            line=0,
            include_type="project",
            project="platform/ci-templates",
            current_version="1.0.0",
            latest_version="2.0.0",
        )
        with open(pipeline, encoding="utf-8") as handle:
            lines = handle.readlines()
        assert _apply_fix_to_file(invalid_line, lines) is False

        next_item = IncludeVersionFix(
            source_file=str(pipeline),
            line=1,
            include_type="project",
            project="platform/ci-templates",
            current_version="1.0.0",
            latest_version="2.0.0",
        )
        lines = ["include:\n", "  - project: other\n", "    ref: 1.0.0\n"]
        assert _apply_fix_to_file(next_item, lines) is False


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

    def test_patches_component_include(self, tmp_path):
        pipeline = tmp_path / ".gitlab-ci.yml"
        pipeline.write_text(
            "include:\n" "  - component: gitlab.com/org/pipeline@1.0.0\n",
            encoding="utf-8",
        )
        fixes = [
            IncludeVersionFix(
                source_file=str(pipeline),
                line=2,
                include_type="component",
                project="gitlab.com/org/pipeline",
                current_version="1.0.0",
                latest_version="2.0.0",
            )
        ]
        applied = apply_include_version_fixes(fixes)
        assert applied
        assert "pipeline@2.0.0" in pipeline.read_text(encoding="utf-8")

    def test_patches_quoted_project_ref(self, tmp_path):
        pipeline = tmp_path / ".gitlab-ci.yml"
        pipeline.write_text(
            "include:\n" "  - project: platform/ci-templates\n" '    ref: "1.0.0"\n',
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
        assert 'ref: "2.0.0"' in pipeline.read_text(encoding="utf-8")

    def test_skips_fix_with_empty_source_file(self):
        fixes = [
            IncludeVersionFix(
                source_file="",
                line=1,
                include_type="project",
                project="platform/ci-templates",
                current_version="1.0.0",
                latest_version="2.0.0",
            )
        ]
        assert apply_include_version_fixes(fixes) == []
