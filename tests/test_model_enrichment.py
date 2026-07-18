from unittest.mock import patch

from src.compliance.model import load_pipeline_entities
from src.compliance.release_cache import ReleaseMetadataCache


class TestLoadPipelineEntitiesEnrichmentFlags:
    def test_skips_include_enrichment_when_disabled(self, tmp_path):
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

        with patch(
            "src.compliance.include_versions.enrich_includes_with_releases"
        ) as enrich:
            with patch(
                "src.compliance.image_versions.enrich_container_images_with_releases"
            ) as image_enrich:
                with patch("src.compliance.gitlab_api.load_api_entities") as api_load:
                    load_pipeline_entities(
                        str(pipeline),
                        token="secret",
                        enrich_includes=False,
                        enrich_images=False,
                        load_api_entities=False,
                    )

        enrich.assert_not_called()
        image_enrich.assert_not_called()
        api_load.assert_not_called()

    def test_enables_include_enrichment_when_requested(self, tmp_path):
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

        with patch(
            "src.compliance.include_versions.enrich_includes_with_releases"
        ) as enrich:
            enrich.return_value = [
                {
                    "include_type": "project",
                    "project": "platform/ci-templates",
                    "version": "1.2.0",
                }
            ]
            with patch("gitlab.Gitlab") as gitlab_cls:
                gitlab_cls.return_value.auth.return_value = None
                load_pipeline_entities(
                    str(pipeline),
                    token="secret",
                    enrich_includes=True,
                    enrich_images=False,
                    load_api_entities=False,
                )

        enrich.assert_called_once()

    def test_reuses_provided_release_cache(self, tmp_path):
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
        cache = ReleaseMetadataCache()

        with patch(
            "src.compliance.include_versions.enrich_includes_with_releases"
        ) as enrich:
            enrich.return_value = [
                {
                    "include_type": "project",
                    "project": "platform/ci-templates",
                    "version": "1.2.0",
                }
            ]
            with patch("gitlab.Gitlab") as gitlab_cls:
                gitlab_cls.return_value.auth.return_value = None
                load_pipeline_entities(
                    str(pipeline),
                    token="secret",
                    enrich_includes=True,
                    enrich_images=False,
                    load_api_entities=False,
                    cache=cache,
                )

        assert enrich.call_args.kwargs["cache"] is cache
