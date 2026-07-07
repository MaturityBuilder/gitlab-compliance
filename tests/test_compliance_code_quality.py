import json

from src.compliance.models import ComplianceResult, ScenarioResult
from src.compliance.render import (
    _fingerprint,
    _map_severity,
    _parse_locations,
    render_compliance_code_quality,
)


def _result(*scenarios: ScenarioResult) -> ComplianceResult:
    return ComplianceResult(
        success=all(s.status == "passed" for s in scenarios),
        exit_code=0 if all(s.status == "passed" for s in scenarios) else 1,
        scenario_results=list(scenarios),
        scenarios=len(scenarios),
        passed=sum(1 for s in scenarios if s.status == "passed"),
        failed=sum(1 for s in scenarios if s.status == "failed"),
        skipped=sum(1 for s in scenarios if s.status == "skipped"),
    )


class TestParseLocations:
    def test_extracts_path_and_line(self):
        message = (
            "Entities missing property: build (examples/sample-files/.gitlab-ci.yml:12)"
        )
        assert _parse_locations(message, ".gitlab-ci.yml") == [
            ("examples/sample-files/.gitlab-ci.yml", 12)
        ]

    def test_multiple_entity_refs(self):
        message = (
            "Failures: build (examples/sample-files/.gitlab-ci.yml:12), "
            "test (examples/sample-files/.gitlab-ci.yml:20)"
        )
        assert _parse_locations(message, ".gitlab-ci.yml") == [
            ("examples/sample-files/.gitlab-ci.yml", 12),
            ("examples/sample-files/.gitlab-ci.yml", 20),
        ]

    def test_fallback_when_no_location(self):
        assert _parse_locations(
            "API connection info not provided", "ci/.gitlab-ci.yml"
        ) == [("ci/.gitlab-ci.yml", 1)]


class TestSeverityMapping:
    def test_high_maps_to_major(self):
        assert _map_severity("failed", "HIGH") == "major"

    def test_skipped_is_info(self):
        assert _map_severity("skipped", "CRITICAL") == "info"

    def test_pass_through_gitlab_levels(self):
        assert _map_severity("failed", "critical") == "critical"


class TestRenderComplianceCodeQuality:
    def test_failed_scenario_produces_valid_finding(self):
        result = _result(
            ScenarioResult(
                feature="image-pinning.feature",
                name="Job images must not use the latest tag",
                status="failed",
                message="Entities where image must not match: build (examples/sample-files/.gitlab-ci.yml:12)",
                policy_id="GLCI-IMAGE-PINNING-001",
                severity="HIGH",
            )
        )
        payload = json.loads(
            render_compliance_code_quality(
                result, "examples/sample-files/.gitlab-ci.yml"
            )
        )
        assert len(payload) == 1
        finding = payload[0]
        assert finding["check_name"] == "GLCI-IMAGE-PINNING-001"
        assert finding["severity"] == "major"
        assert finding["location"]["path"] == "examples/sample-files/.gitlab-ci.yml"
        assert finding["location"]["lines"]["begin"] == 12
        assert set(finding) >= {
            "description",
            "check_name",
            "fingerprint",
            "severity",
            "location",
        }

    def test_multiple_locations_produce_multiple_findings(self):
        result = _result(
            ScenarioResult(
                feature="failing.feature",
                name="Multiple failures",
                status="failed",
                message="Failures: a (.gitlab-ci.yml:1), b (.gitlab-ci.yml:2)",
                policy_id="TEST-001",
            )
        )
        payload = json.loads(render_compliance_code_quality(result, ".gitlab-ci.yml"))
        assert len(payload) == 2
        assert payload[0]["location"]["lines"]["begin"] == 1
        assert payload[1]["location"]["lines"]["begin"] == 2

    def test_skipped_scenario_included_with_info_severity(self):
        result = _result(
            ScenarioResult(
                feature="skip.feature",
                name="Skipped scenario",
                status="skipped",
                message="No entities matched filter",
                policy_id="TEST-SKIP",
            )
        )
        payload = json.loads(render_compliance_code_quality(result, ".gitlab-ci.yml"))
        assert len(payload) == 1
        assert payload[0]["severity"] == "info"

    def test_passed_scenarios_omitted(self):
        result = _result(
            ScenarioResult(
                feature="passing.feature",
                name="Passing",
                status="passed",
                policy_id="TEST-PASS",
            )
        )
        payload = json.loads(render_compliance_code_quality(result, ".gitlab-ci.yml"))
        assert payload == []

    def test_fingerprint_is_stable(self):
        first = _fingerprint("TEST", "file.yml", 10, "message")
        second = _fingerprint("TEST", "file.yml", 10, "message")
        assert first == second

    def test_output_has_no_bom_and_paths_are_normalized(self):
        result = _result(
            ScenarioResult(
                feature="failing.feature",
                name="Failure",
                status="failed",
                message="build (./.gitlab-ci.yml:5)",
                policy_id="TEST",
            )
        )
        raw = render_compliance_code_quality(result, ".gitlab-ci.yml")
        assert not raw.startswith("\ufeff")
        payload = json.loads(raw)
        assert payload[0]["location"]["path"] == "gitlab-ci.yml"
