# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.2] — 2026-08-12

### Added
- Full PyPI metadata (classifiers, URLs, keywords, SPDX license)
- `MANIFEST.in` for complete sdists

### Fixed
- Packaging ready for `pip install prism-eval` from PyPI / Git / release wheel

## [0.2.1] — 2026-08-12

### Added
- `SECURITY.md`, `SUPPORT.md`, `CHANGELOG.md`, threat model, API stability policy
- Immutable `AuditReceipt` with blake2b seal + CLI `--audit-receipt`
- Expanded builtin corpus (HTML injection, currency distractor, format, negative AGI, 32 digit-fuzz cases)
- Optional FinancePackBench-G4 adapter (`load_financepack_g4_cases`)
- Release workflow with wheel/sdist, CycloneDX SBOM, provenance attestations, PyPI publish
- Dependabot, CONTRIBUTING, Code of Conduct, PyPI publishing runbook

### Security
- Documented coordinated disclosure and G4 fail-closed defaults
- CI asserts empty-agent fail-closed + audit receipt verify

## [0.2.0] — 2026-08-12

### Added
- Attack-aware security oracle (digit drop, injection followed, layout shift)
- G4 case model: `severity`, `expected_behavior`, `injected_wrong`, `critical_fields`
- Typed `SuiteReport` / `CaseResult` with false-accept and G4 invariant fields
- Sync + HTTP agent adapters, timeouts, concurrency
- CLI: `--min-determinism`, `--min-pass-rate`, `--junit`, `--sarif`, `--no-upsell`
- Streamlit demo and GitHub Pages interactive demo
- Top-level `prism_eval` import surface

### Security
- Suite gate requires zero critical false accepts (`g4_invariant_held`)

## [0.1.0] — 2026-08-11

### Added
- Initial Prism-Eval engine, evaluators, CLI, builtin/ugly corpora

[Unreleased]: https://github.com/insightitsGit/prism-eval/compare/v0.2.2...HEAD
[0.2.2]: https://github.com/insightitsGit/prism-eval/releases/tag/v0.2.2
[0.2.1]: https://github.com/insightitsGit/prism-eval/releases/tag/v0.2.1
[0.2.0]: https://github.com/insightitsGit/prism-eval/releases/tag/v0.2.0
[0.1.0]: https://github.com/insightitsGit/prism-eval/releases/tag/v0.1.0
