"""Compliance result models."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ScenarioResult:
    feature: str
    name: str
    status: str
    message: str = ""
    policy_id: str = ""
    title: str = ""
    description: str = ""
    severity: str = ""


@dataclass
class ComplianceResult:
    success: bool
    exit_code: int
    features: int = 0
    scenarios: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    scenario_results: list[ScenarioResult] = field(default_factory=list)
