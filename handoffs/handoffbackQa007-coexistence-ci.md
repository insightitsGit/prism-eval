# Handoff back: Coexistence CI

**ID:** HO-prism_eval-007  
**Product file:** `handoffbackQa007-coexistence-ci.md`  
**Date:** 2026-08-12  
**From:** dev-agent  
**To:** Senior QA  
**Status:** Ready for QA

## Summary

Added GitHub Actions job `coexistence` in `.github/workflows/ci.yml` that installs `prism-eval` then PyPI `prismmanifest>=0.3.4`, asserts imports, fail-closed CLI exit `1`, and that the built wheel does not contain `prismmanifest/`.

## Tasks

- [x] **T1:** CI steps: install both, import `PrismEvalEngine`, CLI exit 1 on builtin empty agent
- [x] **T2:** Assert `importlib.metadata.version("prismmanifest")` + site-packages path
- [x] **T3:** Wired on PR/push; `continue-on-error: false` (job fails hard)

## Depends on

handoffQa001 (namespace relocation) — landed in same change set as 0.3.0.
