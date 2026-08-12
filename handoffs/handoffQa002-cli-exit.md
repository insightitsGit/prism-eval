# Handoff: Align CLI exit code with suite_passed

**ID:** HO-prism_eval-002  
**Product file:** `handoffQa002-cli-exit.md`  
**Project:** prism_eval (Prism-Eval)  
**Date:** 2026-08-12  
**From:** Senior QA / Architect  
**To:** dev-agent  
**Priority:** P1  
**Status:** Ready for QA

## Context

`_exit_code` can return `0` while the printed Result is `FAIL` when override flags widen the gate.  
Bug: `C:\code\QA\projects\prism_eval\bugs\BUG-prism_eval-002-cli-exit-alignment.md`

## Objective

Default process exit status must match `SuiteReport.suite_passed`. Overrides stay explicit and documented.

## Tasks

- [ ] **T1:** Default: `return 0 if report.suite_passed else 1`.
- [ ] **T2:** Document `--no-fail-on-critical` / `--no-fail-on-false-accept` as wideners that may exit 0 on FAIL summaries.
- [ ] **T3:** Unit tests for default alignment + override path.

## Constraints

- Do not weaken default fail-closed behavior (empty agent on builtin → non-zero).
- Prefer single source of truth (`suite_passed`) then apply override masks.
- Hand back under `handoffs/handoffbackQa002-*.md` + QA `handoffs-back/`.

## Acceptance Criteria

- [ ] Empty/identity agent, defaults, corpus `builtin` → exit ≠ 0 and `suite_passed is False`
- [ ] Override path documented + tested
- [ ] Existing CLI tests still green

## Related

- QA: `...\handoffs\HO-prism_eval-002-cli-exit-alignment.md`
