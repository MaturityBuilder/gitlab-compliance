from unittest.mock import patch

from src.compliance.container_fix import ContainerImageFix
from src.compliance.include_fix import IncludeVersionFix
from src.compliance.supply_chain_fix import apply_supply_chain_fixes


class TestApplySupplyChainFixes:
    def test_applies_include_and_image_fixes(self):
        include_fix = IncludeVersionFix(
            source_file="ci.yml",
            line=2,
            include_type="project",
            project="platform/ci-templates",
            current_version="1.0.0",
            latest_version="2.0.0",
        )
        image_fix = ContainerImageFix(
            source_file="ci.yml",
            line=5,
            parent_job="scan",
            image_source="job",
            current_image="python:3.12.0",
            fixed_image="python@sha256:abc123",
        )
        entities = {"includes": [], "container_images": []}

        with (
            patch(
                "src.compliance.supply_chain_fix.load_pipeline_entities",
                return_value=entities,
            ) as load_entities,
            patch(
                "src.compliance.supply_chain_fix.collect_include_version_fixes",
                return_value=[include_fix],
            ),
            patch(
                "src.compliance.supply_chain_fix.apply_include_version_fixes",
                return_value=[include_fix],
            ),
            patch(
                "src.compliance.supply_chain_fix.collect_container_image_fixes",
                return_value=[image_fix],
            ),
            patch(
                "src.compliance.supply_chain_fix.apply_container_image_fixes",
                return_value=[image_fix],
            ),
        ):
            messages = apply_supply_chain_fixes(
                pipeline_file="ci.yml",
                include_nested=True,
                gitlab_url=None,
                token="secret",
                project=None,
                group=None,
            )

        assert load_entities.call_count == 2
        assert any(
            "Fixed include platform/ci-templates" in message for message in messages
        )
        assert any("Fixed image python:3.12.0" in message for message in messages)

    def test_reloads_entities_after_include_fixes(self):
        include_fix = IncludeVersionFix(
            source_file="ci.yml",
            line=2,
            include_type="project",
            project="platform/ci-templates",
            current_version="1.0.0",
            latest_version="2.0.0",
        )
        first_entities = {"includes": [{"project": "platform/ci-templates"}]}
        second_entities = {"includes": [], "container_images": []}

        with (
            patch(
                "src.compliance.supply_chain_fix.load_pipeline_entities",
                side_effect=[first_entities, second_entities],
            ) as load_entities,
            patch(
                "src.compliance.supply_chain_fix.collect_include_version_fixes",
                return_value=[include_fix],
            ),
            patch(
                "src.compliance.supply_chain_fix.apply_include_version_fixes",
                return_value=[include_fix],
            ),
            patch(
                "src.compliance.supply_chain_fix.collect_container_image_fixes",
                return_value=[],
            ),
            patch(
                "src.compliance.supply_chain_fix.apply_container_image_fixes",
                return_value=[],
            ),
        ):
            apply_supply_chain_fixes(
                pipeline_file="ci.yml",
                include_nested=False,
                gitlab_url="https://gitlab.com",
                token="secret",
                project="group/project",
                group=None,
            )

        assert load_entities.call_count == 2

    def test_no_messages_when_nothing_to_fix(self):
        entities = {"includes": [], "container_images": []}

        with (
            patch(
                "src.compliance.supply_chain_fix.load_pipeline_entities",
                return_value=entities,
            ) as load_entities,
            patch(
                "src.compliance.supply_chain_fix.collect_include_version_fixes",
                return_value=[],
            ),
            patch(
                "src.compliance.supply_chain_fix.apply_include_version_fixes",
                return_value=[],
            ),
            patch(
                "src.compliance.supply_chain_fix.collect_container_image_fixes",
                return_value=[],
            ),
            patch(
                "src.compliance.supply_chain_fix.apply_container_image_fixes",
                return_value=[],
            ),
        ):
            messages = apply_supply_chain_fixes(
                pipeline_file="ci.yml",
                include_nested=True,
                gitlab_url=None,
                token="secret",
                project=None,
                group=None,
            )

        assert messages == []
        assert load_entities.call_count == 1
