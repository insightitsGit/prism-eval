"""
Optional adapter to FinancePackBench-G4 / CudaDesign prismmanifest.bench.g4_suite.

When a full PrismManifest install exposes ``build_g4_cases``, this module projects
those cases into Prism-Eval ``AdversarialCase`` objects. Otherwise callers use
corpus token ``builtin`` / ``enterprise``.
"""

from __future__ import annotations

from typing import Any

from prismmanifest.bench.g4_suite import AdversarialCase, case_from_mapping


def financepack_g4_available() -> bool:
    try:
        mod = __import__("prismmanifest.bench.g4_suite.cases", fromlist=["build_g4_cases"])
        return callable(getattr(mod, "build_g4_cases", None))
    except Exception:
        return False


def load_financepack_g4_cases(*, include_custom: bool = False) -> list[AdversarialCase]:
    """
    Load cases from an installed FinancePackBench-G4 ``build_g4_cases()`` catalog.

    Raises ImportError when the full suite is not installed.
    """
    try:
        mod = __import__("prismmanifest.bench.g4_suite.cases", fromlist=["build_g4_cases"])
        build_g4_cases = getattr(mod, "build_g4_cases", None)
        if not callable(build_g4_cases):
            raise AttributeError("build_g4_cases missing")
    except Exception as exc:  # noqa: BLE001
        raise ImportError(
            "FinancePackBench-G4 full suite not available. "
            "Use corpus token 'builtin' / 'enterprise', or install the full "
            "prismmanifest package that exposes build_g4_cases."
        ) from exc

    raw_cases = build_g4_cases()
    out: list[AdversarialCase] = []
    for case in raw_cases:
        if getattr(case, "custom", None) is not None and not include_custom:
            continue
        expected_gate = getattr(case, "expected_gate", "")
        expect_group3 = getattr(case, "expected_group3_execution", None)
        behavior = (
            "match_ground_truth"
            if expected_gate == "PASS" and expect_group3
            else "never_false_accept"
        )
        payload: dict[str, Any] = {
            "id": getattr(case, "test_id", None) or getattr(case, "id", "g4"),
            "attack_type": getattr(case, "failure_category", "g4"),
            "severity": getattr(case, "severity", "critical"),
            "expected_behavior": behavior,
            "input_data": {
                "document": getattr(case, "document", ""),
                "user_request": getattr(case, "user_request", ""),
                "candidate_extraction": getattr(case, "candidate_extraction", {}),
            },
            "ground_truth": getattr(case, "ground_truth", {}) or {},
            "metadata": {
                "expected_gate": expected_gate,
                "expected_group3_execution": expect_group3,
                "source": "financepack_g4",
            },
        }
        out.append(case_from_mapping(payload, fallback_id=str(payload["id"])))
    return out
