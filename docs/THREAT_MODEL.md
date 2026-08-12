# Threat Model — Prism-Eval

**Asset:** Correctness of the pre-deploy adversarial gate for AI agent extractions tool arguments.  
**Primary invariant (G4):** Critical poisoned parameters must never look like a successful extraction (`never_false_accept`).

## Stakeholders

| Actor | Goal |
|-------|------|
| Developer | Catch agent regressions before merge |
| Attacker (doc/author) | Inject instructions or distractor numbers into source documents |
| Attacker (supply chain) | Tamper with published wheels / CI artifacts |
| Enterprise buyer | Evidence that eval runs are auditable and fail-closed |

## Trust boundaries

```text
[Adversarial corpus] --untrusted--> [PrismEvalEngine] --calls--> [Agent under test]
                                         |
                                         v
                              [SuiteReport + AuditReceipt]
                                         |
                                         v
                              [CI exit code / JUnit / SARIF]
```

- Corpus files are **untrusted input** (JSON only; no code execution from corpus).
- Agent callables / HTTP agents are **untrusted**; timeouts apply.
- Report consumers (CI) trust the local process that ran the suite.

## Threats & mitigations

| ID | Threat | Mitigation |
|----|--------|------------|
| T1 | Agent follows prompt injection; suite still PASSes | Attack-aware oracle + `never_false_accept` + critical false-accept gate |
| T2 | Digit truncation (`450000`→`45000`) missed | Canonical digit compare + truncation detector |
| T3 | Legitimate `$0` false-fails | Zero allowed only when ground truth is zero |
| T4 | Hung / slow agent blocks CI | Per-case `timeout_s`, concurrency semaphore |
| T5 | CI soft-fails critical attacks | Default exit policy fails on critical false accepts |
| T6 | Schema drift across releases | `schema_contract_hash` over field names/types |
| T7 | Tampered release wheel | GitHub Actions + trusted publishing; optional SBOM attach |
| T8 | Audit denial (“we never ran eval”) | Immutable audit receipts (`AuditReceipt`) with content hashes |

## Non-goals

- Prism-Eval does **not** replace runtime zero-trust enforcement (Prism-Shield / ParameterManifest gate).
- It does **not** claim NLP-perfect injection detection; it claims **oracle checks against ground truth and injected targets**.
- Browser demo (`docs/index.html`) is educational; Streamlit/`PrismEvalEngine` is authoritative.

## Residual risk

Model providers and agent frameworks can change behavior between eval and deploy. Mitigate with:

1. Eval in CI on every PR  
2. Runtime Shield/gateway in production  
3. Periodic corpus expansion against new attack families  
