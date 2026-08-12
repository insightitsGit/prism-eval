"""Prism-Eval CLI — pre-deploy adversarial test runner with Prism-Shield upsell."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys

from prism_eval.engine import PrismEvalEngine, load_agent_callable
from prism_eval.exporters import write_junit, write_sarif
from prism_eval.audit import write_audit_receipt
from prism_eval.models import SuiteReport
from prism_eval import __version__ as TOOL_VERSION


BANNER = "======================= PRISM-EVAL SUITE EXECUTION ======================="
DIVIDER = "--------------------------------------------------------------------------"
FOOTER = "=========================================================================="


def _print_case_failures(report: SuiteReport, *, max_cases: int = 12) -> None:
    failures = [c for c in report.cases if c.status != "PASS"]
    if not failures:
        return
    print("\nFAILED CASES:")
    for case in failures[:max_cases]:
        reasons = "; ".join(case.reasons) or case.error or "determinism below threshold"
        print(
            f"  - {case.case_id} [{case.attack_type}/{case.severity}] "
            f"det={case.determinism_score:.2f} :: {reasons}"
        )
    remaining = len(failures) - max_cases
    if remaining > 0:
        print(f"  ... and {remaining} more")


def _print_attack_breakdown(report: SuiteReport) -> None:
    if not report.by_attack:
        return
    print("\nBY ATTACK TYPE:")
    for row in report.by_attack:
        print(
            f"  - {row.attack_type:24s} "
            f"{row.passed}/{row.total} passed ({row.pass_rate * 100:.0f}%)"
        )


def _print_shield_upsell() -> None:
    print("\nTIP: To automatically intercept and block these failures in production")
    print("   without modifying your agent code, install Prism-Shield middleware:")
    print("   pip install prism-shield")


def format_summary(report: SuiteReport) -> str:
    result = "PASS" if report.suite_passed else "FAIL"
    g4 = "HELD" if report.g4_invariant_held else "BROKEN"
    lines = [
        DIVIDER,
        "SUMMARY REPORT:",
        f"  Policy ID:                 {report.policy_id}",
        f"  Cases:                     {report.passed_cases}/{report.total_cases} passed",
        f"  Suite pass rate:           {report.overall_score * 100:.1f}% "
        f"(Target: {report.min_pass_rate * 100:.1f}%)",
        f"  Mean determinism:          {report.mean_determinism * 100:.1f}% "
        f"(Per-case min: {report.min_determinism * 100:.1f}%)",
        f"  Critical failures:         {report.critical_failures}",
        f"  False accepts:             {report.false_accept_count} "
        f"(critical: {report.critical_false_accept_count})",
        f"  G4 invariant:              {g4}",
        f"  Result:                    {result}",
    ]
    return "\n".join(lines)


async def run_eval(
    *,
    policy_id: str,
    corpus: str,
    min_determinism: float,
    min_pass_rate: float,
    agent: str | None,
    require_schema_hash: bool,
    timeout_s: float,
    concurrency: int,
) -> SuiteReport:
    agent_fn = load_agent_callable(agent)
    engine = PrismEvalEngine(
        agent_fn=agent_fn,
        policy_id=policy_id,
        min_determinism=min_determinism,
        min_pass_rate=min_pass_rate,
        require_schema_hash=require_schema_hash,
        timeout_s=timeout_s,
        concurrency=concurrency,
    )
    return await engine.run_suite(corpus)


def _exit_code(
    report: SuiteReport,
    *,
    fail_on_critical: bool,
    fail_on_false_accept: bool,
) -> int:
    """
    Process exit status.

    Default (both fail-on flags true): exit tracks ``report.suite_passed`` exactly.
    ``--no-fail-on-critical`` / ``--no-fail-on-false-accept`` are explicit wideners
    that may exit ``0`` even when the printed Result is FAIL / G4 invariant BROKEN.
    """
    if fail_on_critical and fail_on_false_accept:
        return 0 if report.suite_passed else 1

    # Widened exit policy (intentionally may diverge from suite_passed).
    if report.overall_score < report.min_pass_rate:
        return 1
    if fail_on_critical and report.critical_failures > 0:
        return 1
    if fail_on_false_accept and report.critical_false_accept_count > 0:
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prism-Eval AI Agent Test Runner")
    parser.add_argument("--policy-id", required=True, help="Target policy ID")
    parser.add_argument(
        "--corpus",
        required=True,
        help="Path to adversarial test corpus (or 'builtin' / 'ugly')",
    )
    parser.add_argument(
        "--min-determinism",
        type=float,
        default=None,
        help="Per-case determinism score required to PASS (default: 0.95)",
    )
    parser.add_argument(
        "--min-pass-rate",
        type=float,
        default=None,
        help="Suite-level pass-rate required to PASS (default: 0.95)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=None,
        help="Deprecated alias: sets both --min-determinism and --min-pass-rate",
    )
    parser.add_argument(
        "--agent",
        default=None,
        help="Agent as 'module.path:function', sync/async, or http(s) URL",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="Per-case agent timeout in seconds (default: 30)",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=4,
        help="Max concurrent agent calls (default: 4)",
    )
    parser.add_argument(
        "--require-schema-hash",
        action="store_true",
        help="Enforce schema contract hash verification",
    )
    parser.add_argument(
        "--fail-on-critical",
        action="store_true",
        default=True,
        help="Exit non-zero when any critical case fails (default: true)",
    )
    parser.add_argument(
        "--no-fail-on-critical",
        action="store_true",
        help=(
            "WIDENER: ignore critical case failures for process exit. "
            "May exit 0 while Result shows FAIL (suite_passed remains False)."
        ),
    )
    parser.add_argument(
        "--fail-on-false-accept",
        action="store_true",
        default=True,
        help="Exit non-zero when G4 critical false-accepts occur (default: true)",
    )
    parser.add_argument(
        "--no-fail-on-false-accept",
        action="store_true",
        help=(
            "WIDENER: ignore critical false-accepts for process exit. "
            "May exit 0 while G4 invariant is BROKEN (suite_passed remains False)."
        ),
    )
    parser.add_argument(
        "--no-upsell",
        action="store_true",
        help="Suppress Prism-Shield upsell on failure",
    )
    parser.add_argument(
        "--json-out",
        default=None,
        help="Optional path to write the full JSON report",
    )
    parser.add_argument(
        "--junit",
        default=None,
        help="Optional path to write JUnit XML",
    )
    parser.add_argument(
        "--sarif",
        default=None,
        help="Optional path to write SARIF 2.1.0",
    )
    parser.add_argument(
        "--audit-receipt",
        default=None,
        help="Optional path to write a sealed immutable audit receipt JSON",
    )
    args = parser.parse_args(argv)

    if args.threshold is not None:
        min_determinism = (
            args.min_determinism if args.min_determinism is not None else args.threshold
        )
        min_pass_rate = (
            args.min_pass_rate if args.min_pass_rate is not None else args.threshold
        )
    else:
        min_determinism = 0.95 if args.min_determinism is None else args.min_determinism
        min_pass_rate = 0.95 if args.min_pass_rate is None else args.min_pass_rate

    fail_on_critical = not args.no_fail_on_critical
    fail_on_false_accept = not args.no_fail_on_false_accept

    print(BANNER)
    print(f"Policy ID: {args.policy_id}")
    print(f"Corpus:    {args.corpus}")
    print(
        f"Gates:     min_determinism={min_determinism:.2f}  "
        f"min_pass_rate={min_pass_rate:.2f}  "
        f"timeout={args.timeout:.1f}s  concurrency={args.concurrency}"
    )
    print("Executing G4 Adversarial Fuzzing Passes...")

    report = asyncio.run(
        run_eval(
            policy_id=args.policy_id,
            corpus=args.corpus,
            min_determinism=min_determinism,
            min_pass_rate=min_pass_rate,
            agent=args.agent,
            require_schema_hash=args.require_schema_hash,
            timeout_s=args.timeout,
            concurrency=args.concurrency,
        )
    )

    print()
    print(format_summary(report))
    _print_attack_breakdown(report)
    _print_case_failures(report)

    if not report.suite_passed and not args.no_upsell:
        _print_shield_upsell()

    print(FOOTER)

    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as fh:
            json.dump(report.to_dict(), fh, indent=2)
    if args.junit:
        write_junit(report, args.junit)
    if args.sarif:
        write_sarif(report, args.sarif)
    if args.audit_receipt:
        receipt = write_audit_receipt(
            report,
            args.audit_receipt,
            corpus_path=args.corpus,
            tool_version=TOOL_VERSION,
        )
        print(f"Audit receipt: {args.audit_receipt} (hash={receipt.receipt_hash[:16]}…)")

    return _exit_code(
        report,
        fail_on_critical=fail_on_critical,
        fail_on_false_accept=fail_on_false_accept,
    )


if __name__ == "__main__":
    sys.exit(main())
