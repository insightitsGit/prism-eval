"""Immutable audit receipts for Prism-Eval suite runs."""

from __future__ import annotations

import hashlib
import json
import platform
import time
import uuid
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Union

from pydantic import BaseModel, Field

from prism_eval.models import SuiteReport


def _canonical_bytes(payload: Mapping[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode(
        "utf-8"
    )


def content_hash(payload: Mapping[str, Any]) -> str:
    return hashlib.blake2b(_canonical_bytes(payload), digest_size=32).hexdigest()


class AuditReceipt(BaseModel):
    """
    Tamper-evident record of a single suite execution.

    ``receipt_hash`` covers all fields except itself — recompute to verify.
    """

    receipt_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    schema_version: str = "1.0.0"
    created_at_unix: float = Field(default_factory=time.time)
    policy_id: str
    corpus_path: str
    corpus_fingerprint: str = ""
    tool_version: str = ""
    python_version: str = Field(default_factory=lambda: platform.python_version())
    platform: str = Field(default_factory=lambda: platform.platform())
    min_determinism: float
    min_pass_rate: float
    suite_passed: bool
    g4_invariant_held: bool
    overall_score: float
    mean_determinism: float
    total_cases: int
    passed_cases: int
    failed_cases: int
    critical_failures: int
    critical_false_accept_count: int
    false_accept_count: int
    report: Dict[str, Any]
    receipt_hash: str = ""

    def compute_hash(self) -> str:
        payload = self.model_dump()
        payload.pop("receipt_hash", None)
        return content_hash(payload)

    def seal(self) -> "AuditReceipt":
        self.receipt_hash = self.compute_hash()
        return self

    def verify(self) -> bool:
        if not self.receipt_hash:
            return False
        return self.receipt_hash == self.compute_hash()


def fingerprint_corpus(corpus_path: str) -> str:
    """Stable fingerprint for builtin tokens or on-disk corpus files."""
    token = (corpus_path or "").strip().lower()
    if token in {"builtin", "g4", "default", "ugly", "ugly_corpus"}:
        return content_hash({"corpus_token": token})

    root = Path(corpus_path)
    if not root.exists():
        return content_hash({"missing": corpus_path})

    files: list[Path]
    if root.is_dir():
        files = sorted(p for p in root.rglob("*") if p.suffix.lower() in {".json", ".jsonl"})
    else:
        files = [root]

    digests = []
    for fp in files:
        digests.append(
            {
                "path": str(fp.as_posix()),
                "sha256": hashlib.sha256(fp.read_bytes()).hexdigest(),
            }
        )
    return content_hash({"files": digests})


def build_audit_receipt(
    report: SuiteReport,
    *,
    corpus_path: str,
    tool_version: str = "",
) -> AuditReceipt:
    receipt = AuditReceipt(
        policy_id=report.policy_id,
        corpus_path=corpus_path,
        corpus_fingerprint=fingerprint_corpus(corpus_path),
        tool_version=tool_version,
        min_determinism=report.min_determinism,
        min_pass_rate=report.min_pass_rate,
        suite_passed=report.suite_passed,
        g4_invariant_held=report.g4_invariant_held,
        overall_score=report.overall_score,
        mean_determinism=report.mean_determinism,
        total_cases=report.total_cases,
        passed_cases=report.passed_cases,
        failed_cases=report.failed_cases,
        critical_failures=report.critical_failures,
        critical_false_accept_count=report.critical_false_accept_count,
        false_accept_count=report.false_accept_count,
        report=report.to_dict(),
    )
    return receipt.seal()


def write_audit_receipt(
    report: SuiteReport,
    path: Union[str, Path],
    *,
    corpus_path: str,
    tool_version: str = "",
) -> AuditReceipt:
    """Write a sealed audit receipt JSON file and return the receipt."""
    path = Path(path)
    receipt = build_audit_receipt(
        report, corpus_path=corpus_path, tool_version=tool_version
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(receipt.model_dump(), indent=2), encoding="utf-8")
    return receipt


def load_audit_receipt(path: Union[str, Path]) -> AuditReceipt:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return AuditReceipt.model_validate(data)
