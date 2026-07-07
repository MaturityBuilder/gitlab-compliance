from src.compliance.models import ComplianceResult, ScenarioResult
from src.compliance.render import (
    render_compliance_html,
    render_compliance_markdown,
    render_compliance_mr_comment,
    render_compliance_report,
)


def _failed_result() -> ComplianceResult:
    scenario = ScenarioResult(
        feature="failing.feature",
        name="Example failure",
        status="failed",
        message="build (examples/sample-files/.gitlab-ci.yml:12)",
        policy_id="TEST-001",
        title="Example",
        description="Example policy",
        severity="HIGH",
    )
    return ComplianceResult(
        success=False,
        exit_code=1,
        scenario_results=[scenario],
        scenarios=1,
        passed=0,
        failed=1,
        skipped=0,
    )


class TestRenderComplianceFormats:
    def test_markdown_report_contains_summary(self):
        text = render_compliance_markdown(
            _failed_result(),
            "examples/sample-files/.gitlab-ci.yml",
            "tests/compliance_policies/failing",
        )
        assert "GitLab CI Compliance Report" in text
        assert "FAIL" in text

    def test_html_report_contains_title(self):
        html = render_compliance_html(
            _failed_result(),
            "examples/sample-files/.gitlab-ci.yml",
            "tests/compliance_policies/failing",
        )
        assert "Compliance" in html
        assert "<html" in html.lower()

    def test_mr_comment_contains_details_block(self):
        comment = render_compliance_mr_comment(
            _failed_result(),
            "examples/sample-files/.gitlab-ci.yml",
            "tests/compliance_policies/failing",
        )
        assert "<details>" in comment
        assert "Compliance failed" in comment

    def test_render_compliance_report_dispatch(self):
        result = _failed_result()
        pipeline = "examples/sample-files/.gitlab-ci.yml"
        policies = "tests/compliance_policies/failing"
        assert render_compliance_report(result, pipeline, policies, "markdown")
        assert render_compliance_report(result, pipeline, policies, "html")
        assert render_compliance_report(result, pipeline, policies, "mr-comment")
        assert render_compliance_report(result, pipeline, policies, "unknown") is None
