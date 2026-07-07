from pathlib import Path

from src.compliance.api_enrichment import policies_require_api_enrichment

REPO_ROOT = Path(__file__).resolve().parents[1]


class TestPoliciesRequireApiEnrichment:
    def test_yaml_only_policies_skip_api_enrichment(self, tmp_path):
        policies = tmp_path / "policies"
        policies.mkdir()
        policies.joinpath("jobs.feature").write_text(
            "Feature: Jobs\n"
            "  Scenario: Jobs must define rules\n"
            "    Given I have any job defined\n"
            "    Then it must contain rules\n",
            encoding="utf-8",
        )

        reqs = policies_require_api_enrichment(str(policies))

        assert reqs.enrich_includes is False
        assert reqs.enrich_images is False
        assert reqs.load_api_entities is False

    def test_include_version_policies_require_include_enrichment(self, tmp_path):
        policies = tmp_path / "policies"
        policies.mkdir()
        policies.joinpath("include.feature").write_text(
            "Feature: Includes\n"
            "  Scenario: Includes must be current\n"
            "    Given I have any include with release metadata defined\n"
            "    Then a newer release must not be available\n",
            encoding="utf-8",
        )

        reqs = policies_require_api_enrichment(str(policies))

        assert reqs.enrich_includes is True
        assert reqs.enrich_images is False

    def test_image_pinning_policies_require_image_enrichment(self, tmp_path):
        policies = tmp_path / "policies"
        policies.mkdir()
        policies.joinpath("image.feature").write_text(
            "Feature: Images\n"
            "  Scenario: Images must be current\n"
            "    Given I have any container image with release metadata defined\n"
            "    Then a newer image release must not be available\n",
            encoding="utf-8",
        )

        reqs = policies_require_api_enrichment(str(policies))

        assert reqs.enrich_images is True

    def test_api_settings_require_project_entities(self, tmp_path):
        policies = tmp_path / "policies"
        policies.mkdir()
        policies.joinpath("api.feature").write_text(
            "Feature: API\n"
            "  Scenario: Public jobs disabled\n"
            '    Given I have project setting "public_jobs" defined\n'
            "    Then its value must be false\n",
            encoding="utf-8",
        )

        reqs = policies_require_api_enrichment(str(policies))

        assert reqs.load_api_entities is True

    def test_execution_policy_pack_is_yaml_only(self, tmp_path):
        policies = tmp_path / "policies"
        policies.mkdir()
        source = (
            REPO_ROOT
            / "examples/examples/example-policies"
            / "security"
            / "execution-policy.feature"
        )
        policies.joinpath("execution-policy.feature").write_text(
            source.read_text(encoding="utf-8"),
            encoding="utf-8",
        )

        reqs = policies_require_api_enrichment(str(policies))

        assert reqs.enrich_includes is False
        assert reqs.enrich_images is False
        assert reqs.load_api_entities is False
