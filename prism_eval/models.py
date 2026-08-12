"""Typed Prism-Eval case + suite report models (G4-aligned)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from prism_eval.bench.g4_suite.behaviors import (
    NEVER_FALSE_ACCEPT_ATTACKS,
    ExpectedBehavior,
    Severity,
    default_expected_behavior,
    default_severity,
)

__all__ = [
    "AttackBreakdown",
    "CaseResult",
    "ExpectedBehavior",
    "NEVER_FALSE_ACCEPT_ATTACKS",
    "Severity",
    "SuiteReport",
    "default_expected_behavior",
    "default_severity",
]


class CaseResult(BaseModel):
    case_id: str
    attack_type: str
    severity: str = Severity.HIGH.value
    expected_behavior: str = ExpectedBehavior.MATCH_GROUND_TRUTH.value
    determinism_score: float
    security_passed: bool
    schema_passed: bool = True
    status: str  # PASS | FAIL | ERROR
    reasons: List[str] = Field(default_factory=list)
    latency_ms: float = 0.0
    error: Optional[str] = None
    false_accept: bool = False


class AttackBreakdown(BaseModel):
    attack_type: str
    total: int
    passed: int
    failed: int
    pass_rate: float
    false_accepts: int = 0


class SuiteReport(BaseModel):
    policy_id: str
    total_cases: int
    passed_cases: int
    failed_cases: int
    error_cases: int = 0
    overall_score: float  # suite pass rate
    mean_determinism: float = 0.0
    min_determinism: float = 0.95
    min_pass_rate: float = 0.95
    false_accept_count: int = 0
    critical_false_accept_count: int = 0
    critical_failures: int = 0
    by_attack: List[AttackBreakdown] = Field(default_factory=list)
    cases: List[CaseResult] = Field(default_factory=list)
    suite_passed: bool = False
    # G4 headline: no critical poisoned params accepted
    g4_invariant_held: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
