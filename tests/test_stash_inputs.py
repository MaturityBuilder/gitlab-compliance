"""Unit tests for component input and conditional property helpers."""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from src.compliance.behave_support.steps import when_steps
from src.compliance.stash import (
    get_conditional_property,
    get_inputs,
    input_matches,
    property_matches_conditional,
)


class TestGetInputs:
    def test_reads_values_inputs(self):
        entity = {"values": {"inputs": {"mode": "execute"}}}
        assert get_inputs(entity) == {"mode": "execute"}

    def test_falls_back_to_values_variables(self):
        entity = {"values": {"variables": {"workflow": "trunk"}}}
        assert get_inputs(entity) == {"workflow": "trunk"}

    def test_prefers_inputs_over_variables(self):
        entity = {"values": {"inputs": {"a": "1"}, "variables": {"b": "2"}}}
        assert get_inputs(entity) == {"a": "1"}

    def test_non_dict_values_returns_empty(self):
        assert get_inputs({"values": "x"}) == {}

    def test_missing_values_returns_empty(self):
        assert get_inputs({}) == {}


class TestInputMatches:
    def test_literal(self):
        entity = {"values": {"variables": {"mode": "execute"}}}
        assert input_matches(entity, "mode", "execute") is True
        assert input_matches(entity, "mode", "dry-run") is False

    def test_comma_list(self):
        entity = {"values": {"variables": {"workflow": "main"}}}
        assert input_matches(entity, "workflow", "trunk,main") is True
        assert input_matches(entity, "workflow", "gitops") is False

    def test_regex(self):
        entity = {"values": {"variables": {"ROLE": "backend"}}}
        assert input_matches(entity, "ROLE", r"^(backend|frontend|ops)$") is True
        entity["values"]["variables"]["ROLE"] = "admin"
        assert input_matches(entity, "ROLE", r"^(backend|frontend|ops)$") is False

    def test_missing_input_returns_false(self):
        entity = {"values": {"variables": {"mode": "execute"}}}
        assert input_matches(entity, "missing", "x") is False


class TestGetConditionalProperty:
    def test_prefers_input_over_top_level(self):
        entity = {
            "workflow": "top-level",
            "values": {"variables": {"workflow": "from-inputs"}},
        }
        assert get_conditional_property(entity, "workflow") == "from-inputs"

    def test_falls_back_to_top_level_property(self):
        entity = {"key": "RUNNER", "values": {"value": "docker"}}
        assert get_conditional_property(entity, "key") == "RUNNER"
        assert get_conditional_property(entity, "value") == "docker"


class TestPropertyMatchesConditional:
    def test_matches_literal_via_inputs(self):
        entity = {"values": {"variables": {"workflow": "gitops"}}}
        assert property_matches_conditional(entity, "workflow", "gitops") is True

    def test_matches_comma_list_via_inputs(self):
        entity = {"values": {"variables": {"workflow": "main"}}}
        assert property_matches_conditional(entity, "workflow", "trunk,main") is True

    def test_matches_regex_via_inputs(self):
        entity = {"values": {"variables": {"ROLE": "frontend"}}}
        assert (
            property_matches_conditional(entity, "ROLE", r"^(backend|frontend|ops)$")
            is True
        )

    def test_invalid_regex_raises(self):
        entity = {"values": {"variables": {"ROLE": "backend"}}}
        with pytest.raises(ValueError, match="Invalid regex pattern"):
            property_matches_conditional(entity, "ROLE", "[invalid")


class TestWhenPropertyMatchesConditional:
    def test_filters_component_inputs_dict(self):
        matching = {
            "include_type": "component",
            "values": {"variables": {"workflow": "trunk"}},
        }
        other = {
            "include_type": "component",
            "values": {"variables": {"workflow": "gitops"}},
        }
        context = SimpleNamespace(
            stash=[matching, other],
            scenario_skipped=False,
            step_mode=None,
            scenario=SimpleNamespace(skip=MagicMock()),
        )
        when_steps.when_property_matches_conditional(context, "workflow", "trunk,main")
        assert context.stash == [matching]
