# Handoff: Coexistence CI (prism-eval + prismmanifest)

**ID:** HO-prism_eval-007  
**Product file:** `handoffQa007-coexistence-ci.md`  
**Project:** prism_eval (Prism-Eval)  
**Date:** 2026-08-12  
**From:** Senior QA / Architect  
**To:** test-agent (or dev-agent if owning CI)  
**Priority:** P0  
**Status:** Ready for QA

## Context

BUG-001 only shows when `prismmanifest` is installed and wins `sys.path`. Current CI installs only `.[dev]` and never co-installs the gate package — so the launch blocker cannot ratchet.

Depends on / lands with **handoffQa001**. Job may stay red until namespace fix lands — that is intended.

## Objective

Add CI coverage that fails if `prism-eval` cannot import/run beside `prismmanifest`.

## Tasks

- [ ] **T1:** New CI job or step after install:
  1. `pip install .`
  2. `pip install prismmanifest` (pin known-good version or documented extra)
  3. `python -c "from prism_eval import PrismEvalEngine; print(PrismEvalEngine)"`
  4. `prism-eval --policy-id ci --corpus builtin --no-upsell` → expect exit code `1`
- [ ] **T2:** Optional assert `importlib.metadata.version("prismmanifest")` works and eval still imports.
- [ ] **T3:** Wire into `.github/workflows/ci.yml` on PRs (`continue-on-error: false` after HO-001).

## Constraints

- If PyPI `prismmanifest` is unavailable, pin a wheel URL — do not silently skip forever.
- Do not edit QA tree except handoff-back.

## Acceptance Criteria

- [ ] Coexistence job present on PRs
- [ ] Would fail on current `main` before namespace fix; passes after handoffQa001

## Hand back

Status → `Ready for QA` + `handoffbackQa007-*.md` + QA `handoffs-back/`.

## Related

- QA: `...\handoffs\HO-prism_eval-007-coexistence-ci.md`
- Blocks launch gate in `AGENT-PROTOCOL.md`
