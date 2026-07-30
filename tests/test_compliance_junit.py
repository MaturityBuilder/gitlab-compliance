"""Tests for JUnit XML compliance report output."""

from __future__ import annotations

import xml.etree.ElementTree as ET

from src.compliance.models import ComplianceResult, ScenarioResult
from src.compliance.render import render_compliance_junit, render_compliance_report


def _failed_shell_scenario() -> ScenarioResult:
    return ScenarioResult(
        feature="shell-pinning.feature",
        name="apt packages must be version-pinned",
        status="failed",
        message=(
            "ASSERT FAILED: Job 'build' ci.yml:4: Unpinned apt package install; "
            "Job 'deploy' ci.yml:9: Unpinned apt package install via: extends:build"
        ),
        policy_id="GLCI-SHELL-PIN-005",
        title="apt packages must be version-pinned",
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


class TestRenderComplianceJunit:
    def test_failed_scenario_produces_valid_xml(self):
        xml_text = render_compliance_junit(
            _result(_failed_shell_scenario()),
            "ci.yml",
            suite_name="shell-check",
        )
        assert xml_text.startswith('<?xml version="1.0" encoding="UTF-8"?>')
        root = ET.fromstring(xml_text)
        assert root.tag == "testsuites"
        assert root.attrib["name"] == "shell-check"
        assert root.attrib["failures"] == "1"
        failures = root.findall(".//failure")
        assert len(failures) == 1
        assert "build @ ci.yml:4" in failures[0].text

    def test_skipped_scenario_produces_skipped_element(self):
        xml_text = render_compliance_junit(
            _result(
                ScenarioResult(
                    feature="skip.feature",
                    name="Skipped",
                    status="skipped",
                    message="No entities matched",
                    policy_id="TEST-SKIP",
                )
            ),
            ".gitlab-ci.yml",
        )
        root = ET.fromstring(xml_text)
        assert root.find(".//skipped") is not None

    def test_passed_scenario_has_no_failure_or_skipped(self):
        xml_text = render_compliance_junit(
            _result(
                ScenarioResult(
                    feature="pass.feature",
                    name="Passing",
                    status="passed",
                    policy_id="TEST-PASS",
                )
            ),
            ".gitlab-ci.yml",
        )
        root = ET.fromstring(xml_text)
        assert root.find(".//failure") is None
        assert root.find(".//skipped") is None

    def test_render_compliance_report_dispatch(self):
        result = _result(_failed_shell_scenario())
        assert render_compliance_report(
            result, "ci.yml", "policies", "junit", suite_name="shell-check"
        )

    def test_failures_only_omits_passed_and_skipped(self):
        result = _result(
            _failed_shell_scenario(),
            ScenarioResult(
                feature="pass.feature",
                name="Passing",
                status="passed",
                policy_id="TEST-PASS",
            ),
            ScenarioResult(
                feature="skip.feature",
                name="Skipped",
                status="skipped",
                message="No entities matched",
                policy_id="TEST-SKIP",
            ),
        )
        xml_text = render_compliance_junit(
            result, "ci.yml", suite_name="shell-check", failures_only=True
        )
        root = ET.fromstring(xml_text)
        assert root.attrib["tests"] == "1"
        assert root.attrib["failures"] == "1"
        assert root.attrib["skipped"] == "0"
        assert len(root.findall(".//testcase")) == 1
        assert root.find(".//skipped") is None

        via_report = render_compliance_report(
            result,
            "ci.yml",
            "policies",
            "junit",
            suite_name="shell-check",
            failures_only=True,
        )
        assert via_report is not None
        assert ET.fromstring(via_report).attrib["tests"] == "1"


def test_compliance_markdown_includes_coverage_gaps_and_shell_table():
    from src.compliance.render import (
        render_compliance_html,
        render_compliance_markdown,
        render_compliance_mr_comment,
    )

    result = _result(_failed_shell_scenario())
    result.unresolved_includes = [
        {
            "include_type": "remote",
            "reference": "https://example.com/ci.yml",
            "reason": "fetch_failed",
            "detail": "404",
            "source_file": ".gitlab-ci.yml",
            "line": 2,
        }
    ]
    markdown = render_compliance_markdown(result, "ci.yml", "policies")
    assert "Coverage gaps" in markdown
    assert "Job" in markdown and "Location" in markdown

    html = render_compliance_html(result, "ci.yml", "policies")
    assert "Coverage gaps" in html

    mr = render_compliance_mr_comment(result, "ci.yml", "policies")
    assert "Coverage gaps" in mr
    assert "Unpinned apt package install" in mr
