# API Stability & Semantic Versioning

Prism-Eval follows [SemVer 2.0.0](https://semver.org/).

## Public API (stable within a major version)

Import from `prism_eval` only (stable public surface since 0.3.0):

```python
from prism_eval import PrismEvalEngine, SuiteReport
```

**Breaking (0.3.0):** this package no longer ships a top-level `prismmanifest` tree.
`from prismmanifest.prism_eval import …` is removed so Prism-Eval can coexist with the
gate package `prismmanifest` / Prism-Shield.

Stable symbols:

- `PrismEvalEngine`
- `SuiteReport`, `CaseResult`, `AttackBreakdown`
- `DeterminismEvaluator`, `SecurityEvaluator`, `SecurityEvalResult`
- `ExpectedBehavior`, `Severity`
- `load_agent_callable`, `make_http_agent`, `ensure_async_agent`
- `write_junit`, `write_sarif`
- `write_audit_receipt`, `AuditReceipt` (0.2+)
- CLI entry point: `prism-eval`

## Compatibility promises

| Change type | Version bump |
|-------------|--------------|
| Bug / security fix, no API break | PATCH (`0.2.x`) |
| New optional fields / flags / corpus tokens | MINOR (`0.x.0`) while major is `0` |
| Removing/renaming public symbols, changing report required fields incompatibly | MAJOR |

During **0.x**, MINOR bumps may include deliberate breaking changes; they will be called out in CHANGELOG under **Breaking**.

## Deprecated aliases

- `--threshold` → use `--min-determinism` and `--min-pass-rate`
- `schema_hash_lock` (value payload) → prefer `schema_contract_hash`

## CLI exit codes

Default process exit is `0` iff `SuiteReport.suite_passed` is true.

`--no-fail-on-critical` and `--no-fail-on-false-accept` are **explicit wideners**:
they may yield exit `0` while the printed Result is still `FAIL`. Prefer leaving
defaults on for CI gates.

## Not covered by stability

- Builtin corpus case IDs (may expand; IDs are additive)
- Browser demo JS oracle (educational; Python engine is authoritative)
- Private / underscore-prefixed modules
