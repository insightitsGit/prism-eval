# Handoff: Resolve prismmanifest namespace collision

**ID:** HO-prism_eval-001  
**Product file:** `handoffQa001-namespace-collision.md`  
**Project:** prism_eval (Prism-Eval)  
**Date:** 2026-08-12  
**From:** Senior QA / Architect  
**To:** dev-agent  
**Priority:** P0  
**Status:** Ready for QA

## Context

Full QA (`C:\code\QA\projects\prism_eval\reviews\2026-08-12-full-codebase.md`) confirmed co-installing `prism-eval` with PyPI `prismmanifest` (Prism-Shield dependency) breaks imports and the CLI.

See: `C:\code\QA\projects\prism_eval\bugs\BUG-prism_eval-001-namespace-collision.md`  
Architecture: `...\architecture-gaps\ARCH-prism_eval-001-package-boundary.md`

## Objective

Make `prism-eval` importable and runnable when `prismmanifest` / `prism-shield` are installed in the same environment.

## Background

- This repo currently packages modules under top-level `prismmanifest` and registers  
  `prism-eval = prism_eval.cli:main`.
- The real gate product also owns `prismmanifest`; Python allows only one winner.
- Reproduce: install both packages, run from a directory **other than** this repo root:
  ```text
  python -c "from prism_eval import PrismEvalEngine"
  → ModuleNotFoundError: No module named 'prismmanifest.bench.g4_suite.behaviors'
  ```
- Editable installs from inside this repo can **mask** the bug — always verify from a clean cwd/venv.

## Tasks

- [ ] **T1:** Relocate eval internals out of competing `prismmanifest` package root (prefer under `prism_eval/`).  
  - Acceptance: sdist/wheel no longer installs a replacement `prismmanifest` tree.
- [ ] **T2:** Point console script at `prism_eval.cli:main` (or equivalent non-colliding path).  
  - Acceptance: `prism-eval --help` works with both packages installed.
- [ ] **T3:** Keep FinancePack adapter as optional import of **external** `prismmanifest` when present.  
  - Acceptance: core eval works without it; graceful ImportError when absent.
- [ ] **T4:** Update README / `docs/API_STABILITY.md` import paths; CHANGELOG **Breaking** note.

## Constraints

- Keep preferred surface: `from prism_eval import PrismEvalEngine`.
- Do not fake coexistence (must pass clean venv test).
- Commit/push only if the user asks.
- Do not edit `C:\code\QA\` except writing `projects/prism_eval/handoffs-back/`.

## Acceptance Criteria

- [ ] Clean venv: `pip install .` → imports + CLI + pytest pass
- [ ] Clean venv: `pip install . prismmanifest` → `from prism_eval import PrismEvalEngine` works; empty-agent CLI on `builtin` exits non-zero
- [ ] `import prismmanifest` still resolves to the **gate** package when both installed
- [ ] Unit tests adapted and green

## Verification (QA will re-run)

1. Fresh venv with both packages; import + CLI from `C:\code\QA`.
2. pytest in product repo.
3. Confirm no top-level collision in wheel contents (`*.dist-info` / package list).

## Hand back

1. Set Status → `Ready for QA` or `Blocked`.
2. Write `handoffs/handoffbackQa001-namespace-collision.md` + QA `handoffs-back/HB-prism_eval-001-*.md`.
3. Do **not** close the bug — QA closes after verify.

## Related

- QA mirror: `C:\code\QA\projects\prism_eval\handoffs\HO-prism_eval-001-namespace-collision.md`
- Follow with: `handoffQa007-coexistence-ci.md`
