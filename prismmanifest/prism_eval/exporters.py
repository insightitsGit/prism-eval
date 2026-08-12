"""CI exporters for Prism-Eval suite reports (JUnit XML + SARIF)."""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Union
from xml.dom import minidom

from prismmanifest.prism_eval.models import SuiteReport


def write_junit(report: SuiteReport, path: Union[str, Path]) -> None:
    """Write a JUnit XML report suitable for GitHub Actions / most CI systems."""
    path = Path(path)
    suites = ET.Element(
        "testsuites",
        {
            "name": f"prism-eval:{report.policy_id}",
            "tests": str(report.total_cases),
            "failures": str(report.failed_cases),
            "errors": str(report.error_cases),
        },
    )
    suite = ET.SubElement(
        suites,
        "testsuite",
        {
            "name": report.policy_id,
            "tests": str(report.total_cases),
            "failures": str(report.failed_cases),
            "errors": str(report.error_cases),
        },
    )
    for case in report.cases:
        classname = f"prism_eval.{case.attack_type}"
        tc = ET.SubElement(
            suite,
            "testcase",
            {
                "classname": classname,
                "name": case.case_id,
                "time": f"{max(case.latency_ms, 0.0) / 1000.0:.6f}",
            },
        )
        if case.status == "ERROR":
            err = ET.SubElement(tc, "error", {"message": case.error or "error"})
            err.text = "\n".join(case.reasons) or (case.error or "")
        elif case.status != "PASS":
            fail = ET.SubElement(
                tc,
                "failure",
                {
                    "message": f"{case.attack_type} failed (det={case.determinism_score:.2f})",
                    "type": case.attack_type,
                },
            )
            fail.text = "\n".join(case.reasons) or "case failed"

    rough = ET.tostring(suites, encoding="utf-8")
    pretty = minidom.parseString(rough).toprettyxml(indent="  ", encoding="utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(pretty)


def write_sarif(report: SuiteReport, path: Union[str, Path]) -> None:
    """Write SARIF 2.1.0 for code-scanning style consumption of failed cases."""
    path = Path(path)
    rules = {}
    results = []
    for case in report.cases:
        if case.status == "PASS":
            continue
        rule_id = f"prism-eval/{case.attack_type}"
        if rule_id not in rules:
            rules[rule_id] = {
                "id": rule_id,
                "name": case.attack_type,
                "shortDescription": {"text": f"Prism-Eval {case.attack_type} failure"},
                "defaultConfiguration": {
                    "level": "error" if case.severity == "critical" else "warning"
                },
            }
        level = "error" if case.severity == "critical" or case.status == "ERROR" else "warning"
        message = "; ".join(case.reasons) or case.error or f"{case.case_id} failed"
        results.append(
            {
                "ruleId": rule_id,
                "level": level,
                "message": {"text": f"[{case.case_id}] {message}"},
                "properties": {
                    "case_id": case.case_id,
                    "attack_type": case.attack_type,
                    "severity": case.severity,
                    "determinism_score": case.determinism_score,
                    "false_accept": case.false_accept,
                },
            }
        )

    sarif = {
        "version": "2.1.0",
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "prism-eval",
                        "informationUri": "https://pypi.org/project/prism-eval/",
                        "rules": list(rules.values()),
                    }
                },
                "results": results,
                "properties": {
                    "policy_id": report.policy_id,
                    "overall_score": report.overall_score,
                    "mean_determinism": report.mean_determinism,
                    "false_accept_count": report.false_accept_count,
                    "critical_false_accept_count": report.critical_false_accept_count,
                    "g4_invariant_held": report.g4_invariant_held,
                    "suite_passed": report.suite_passed,
                },
            }
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(sarif, indent=2), encoding="utf-8")
