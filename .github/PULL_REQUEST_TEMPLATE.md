## Summary

<!-- What and why (not just what files changed). -->

## Type of change

- [ ] Bug fix
- [ ] Feature / enhancement
- [ ] Docs / packaging / CI
- [ ] Security hardening

## Checklist

- [ ] Tests added or updated (`pytest tests/test_prism_eval_engine.py`)
- [ ] Did **not** weaken G4 false-accept / critical invariant to greenwash CI
- [ ] `CHANGELOG.md` updated under `[Unreleased]` (if user-facing)
- [ ] No secrets, tokens, or credentials in the diff
- [ ] Security-sensitive changes noted for reviewer attention

## Test plan

<!-- Commands you ran / cases covered -->

```bash
pytest tests/test_prism_eval_engine.py -v
```
