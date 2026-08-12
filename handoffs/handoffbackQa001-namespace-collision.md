# Handoff back: Resolve prismmanifest namespace collision

**ID:** HO-prism_eval-001  
**Product file:** `handoffbackQa001-namespace-collision.md`  
**Date:** 2026-08-12  
**From:** dev-agent  
**To:** Senior QA  
**Status:** Ready for QA

## Summary

Relocated all eval internals under `prism_eval.*` and removed the competing top-level `prismmanifest` package from this distribution (Breaking → **0.3.0**).

## Tasks

- [x] **T1:** Internals under `prism_eval/` (bench, spans, schema, engine, CLI, …). Wheel contains no `prismmanifest/`.
- [x] **T2:** Console script `prism_eval.cli:main`.
- [x] **T3:** `g4_adapter` only dynamically imports **external** `prismmanifest…build_g4_cases`.
- [x] **T4:** README / `docs/API_STABILITY.md` / CHANGELOG **Breaking** updated.

## Verification performed

1. `pytest tests/test_prism_eval_engine.py` → **22 passed**
2. Clean venv from `C:\code\QA`:
   - `pip install .` then `pip install prismmanifest>=0.3.4`
   - `from prism_eval import PrismEvalEngine` OK (`0.3.0`)
   - `prismmanifest` resolves to site-packages gate `0.3.4`
   - empty-agent CLI on `builtin` → **exit=1**
3. Built wheel `prism_eval-0.3.0-py3-none-any.whl` — no `prismmanifest/` members

## Notes for QA

- Do not close BUG-001 until you re-verify coexistence from a clean cwd.
- Follow-on CI ratchet: handoffQa007 / handoffbackQa007.
