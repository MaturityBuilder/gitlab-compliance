from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]

EXAMPLE_YAML_FILES = [
    REPO_ROOT / "example-ci" / "compliance-jobs.yml",
    REPO_ROOT / "example-ci" / ".gitlab-ci.consumer.yml",
    REPO_ROOT / "examples/example-gitlab-execution-policy" / "policy-ci.yml",
    REPO_ROOT / "examples/example-gitlab-execution-policy" / ".gitlab" / "security-policies" / "policy.yml",
]


class TestExampleCiYaml:
    def test_example_yaml_files_parse(self):
        for path in EXAMPLE_YAML_FILES:
            assert path.is_file(), f"missing example file: {path}"
            documents = list(yaml.safe_load_all(path.read_text(encoding="utf-8")))
            assert documents, f"no YAML documents in {path}"
            assert all(doc is not None for doc in documents), f"empty document in {path}"

    def test_compliance_jobs_defines_templates(self):
        data = yaml.safe_load(
            (REPO_ROOT / "example-ci" / "compliance-jobs.yml").read_text(encoding="utf-8")
        )
        assert ".compliance:offline" in data
        assert ".compliance:api" in data
        assert ".compliance:codequality" in data

    def test_pipeline_execution_policy_uses_inject_policy(self):
        data = yaml.safe_load(
            (
                REPO_ROOT
                / "examples/example-gitlab-execution-policy"
                / ".gitlab"
                / "security-policies"
                / "policy.yml"
            ).read_text(encoding="utf-8")
        )
        policy = data["pipeline_execution_policy"][0]
        assert policy["pipeline_config_strategy"] == "inject_policy"
