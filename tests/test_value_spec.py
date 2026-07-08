"""Unit tests for Examples cell value spec matching."""

import pytest

from src.compliance.stash import match_value_spec


class TestMatchValueSpecLiteral:
    def test_exact_match(self):
        assert match_value_spec("prod", "prod") is True

    def test_mismatch(self):
        assert match_value_spec("prod", "uat") is False

    def test_empty_spec_matches_empty(self):
        assert match_value_spec("", "") is True


class TestMatchValueSpecCommaList:
    def test_or_allowlist(self):
        assert match_value_spec("trunk", "trunk,main") is True
        assert match_value_spec("main", "trunk,main") is True
        assert match_value_spec("gitops", "trunk,main") is False

    def test_trimmed_entries(self):
        assert match_value_spec("uat", "prod, uat, dev") is True

    def test_env_allowlist(self):
        assert match_value_spec("prod", "prod,uat,dev") is True
        assert match_value_spec("staging", "prod,uat,dev") is False


class TestMatchValueSpecRegex:
    def test_anchored_alternation(self):
        assert match_value_spec("backend", r"^(backend|frontend|ops)$") is True
        assert match_value_spec("frontend", r"^(backend|frontend|ops)$") is True
        assert match_value_spec("admin", r"^(backend|frontend|ops)$") is False

    def test_pipe_inside_regex_not_comma_list(self):
        spec = r"^(prod|uat|dev)$"
        assert match_value_spec("prod", spec) is True
        assert match_value_spec("uat", spec) is True

    def test_slash_wrapped_pattern(self):
        assert match_value_spec("build", "/^(build|test)$/") is True

    def test_dot_plus_pattern(self):
        assert match_value_spec("my-app", ".+") is True
        assert match_value_spec("", ".+") is False

    def test_invalid_regex_raises(self):
        with pytest.raises(ValueError, match="Invalid regex pattern"):
            match_value_spec("x", "[invalid")


class TestMatchValueSpecEdgeCases:
    def test_none_normalizes_to_empty(self):
        assert match_value_spec(None, "") is True

    def test_bool_normalizes(self):
        assert match_value_spec(True, "true") is True

    def test_comma_in_regex_not_treated_as_list(self):
        assert match_value_spec("a,b", r"^a,b$") is True
