# Publishing `prism-eval` to PyPI

The Release workflow publishes on tag push (`v*`) using either:

1. **Trusted Publishing (OIDC)** — preferred, no long-lived tokens  
2. **API token** — set GitHub Actions secret `PYPI_API_TOKEN` to a PyPI token (`pypi-...`)

## One-time Trusted Publisher setup (required for first upload)

PyPI rejected the v0.2.1 OIDC exchange with `invalid-publisher` until this is registered.

1. Sign in at [https://pypi.org](https://pypi.org)  
2. Open **Your projects → Publishing → Pending publisher** (new project)  
3. Enter exactly:

| Field | Value |
|-------|-------|
| PyPI project name | `prism-eval` |
| Owner | `insightitsGit` |
| Owner id | `295265130` |
| Repository | `prism-eval` |
| Workflow name | `release.yml` |
| Environment name | `pypi` |

4. Save the pending publisher  
5. Re-run the failed `publish-pypi` job on the [v0.2.1 Release workflow](https://github.com/insightitsGit/prism-eval/actions/workflows/release.yml), **or**:

```bash
gh workflow run release.yml -f publish_pypi=true
# or re-run job:
gh run rerun <run-id> --failed
```

### Debugging claims from v0.2.1

```
repository: insightitsGit/prism-eval
repository_owner: insightitsGit
repository_owner_id: 295265130
workflow_ref: .../release.yml@refs/tags/v0.2.1
environment: pypi
```

## API token (recommended for first upload)

### Option A — local upload (fastest)

```powershell
cd c:\code\Prism_Eval
$env:TWINE_USERNAME = "__token__"
$env:TWINE_PASSWORD = "pypi-YOUR_TOKEN_HERE"   # paste full token including pypi- prefix
python -m twine upload dist/*
```

### Option B — GitHub Actions secret

```text
GitHub repo → Settings → Secrets and variables → Actions
Name:  PYPI_API_TOKEN
Value: pypi-AgEIcHlwaS5vcmc...
```

Then re-run the failed publish job:

```powershell
gh run rerun 31571821511 --failed
```

The release job passes `user: __token__` and `password: ${{ secrets.PYPI_API_TOKEN }}` into `pypa/gh-action-pypi-publish`.

## Verify

```bash
pip index versions prism-eval
pip install prism-eval==0.2.2
python -c "import prism_eval; print(prism_eval.__version__)"
```

## Artifacts always produced (even before PyPI is linked)

On each `v*` tag:

- `dist/*.whl` + `dist/*.tar.gz`  
- `sbom.cdx.json` (CycloneDX)  
- GitHub Release attachments  
- Build provenance attestations  
