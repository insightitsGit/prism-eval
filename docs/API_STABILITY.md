# API Stability & Semantic Versioning

Prism-Eval follows [SemVer 2.0.0](https://semver.org/).

## Public API (stable within a major version)

Import from `prism_eval` (preferred) or `prismmanifest.prism_eval`:

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

## Not covered by stability

- Builtin corpus case IDs (may expand; IDs are additive)
- Browser demo JS oracle (educational; Python engine is authoritative)
- Private / underscore-prefixed modules
