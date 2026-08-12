# Handoff back: Align CLI exit code with suite_passed

**ID:** HO-prism_eval-002  
**Product file:** `handoffbackQa002-cli-exit.md`  
**Date:** 2026-08-12  
**From:** dev-agent  
**To:** Senior QA  
**Status:** Ready for QA

## Summary

Default `_exit_code` is now `0 if report.suite_passed else 1`. `--no-fail-on-critical` / `--no-fail-on-false-accept` remain explicit wideners (documented in CLI help + `docs/API_STABILITY.md`) that may exit 0 while Result is FAIL.

## Tasks

- [x] **T1:** Default tracks `suite_passed`
- [x] **T2:** Widener flags documented
- [x] **T3:** Tests:
  - `test_cli_default_exit_tracks_suite_passed_builtin`
  - `test_cli_exit_wideners_may_diverge_from_suite_passed`
  - existing CLI failure test still green

## Verification

Empty/identity agent, defaults, corpus `builtin` → exit `1` and `suite_passed is False` (coexistence + unit tests).
