# Contributing to Prism-Eval

Thanks for helping harden AI agent evaluation.

## Development setup

```bash
git clone https://github.com/insightitsGit/prism-eval.git
cd prism-eval
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -e ".[dev,demo]"
pytest tests/test_prism_eval_engine.py -v
```

## Pull requests

1. Open an issue first for larger design changes  
2. Fork the repo and open a PR against `main` (direct pushes to `main` are restricted)  
3. Keep PRs focused; include tests for oracle / corpus / CLI behavior  
4. Do **not** weaken G4 false-accept criteria to make tests pass  
5. Update `CHANGELOG.md` under `[Unreleased]`  
6. Never commit secrets, API tokens, or credentials  

## Asking questions

Use the **Question** issue template. For enterprise / SLA topics see [SUPPORT.md](SUPPORT.md) or [InsightITS](https://www.insightits.com).

## Security

Report vulnerabilities privately — see [SECURITY.md](SECURITY.md). Do not file public issues for security reports.

## Code style

- Python 3.10+  
- Prefer typed public APIs (`SuiteReport`, `AuditReceipt`)  
- No mocked “fake scores” in CLI paths  

## Release (maintainers)

1. Ensure CI is green on `main`  
2. Update `CHANGELOG.md` + `pyproject.toml` version  
3. Tag: `git tag vX.Y.Z && git push origin vX.Y.Z`  
4. GitHub Actions builds wheels, SBOM, attestations, GitHub Release, and PyPI publish  

PyPI setup: [docs/PYPI_PUBLISHING.md](docs/PYPI_PUBLISHING.md)
