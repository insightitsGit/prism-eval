# Publishing `prism-eval` to PyPI

The Release workflow publishes on tag push (`v*`) using either:

1. **Trusted Publishing (OIDC)** — preferred, no long-lived tokens  
2. **API token** — set GitHub Actions secret `PYPI_API_TOKEN` to a PyPI token (`pypi-...`)

## One-time Trusted Publisher setup (recommended)

1. Create / sign in at [https://pypi.org](https://pypi.org)  
2. Open **Publishing → Pending Publisher** (new project) or project **Settings → Publishing**  
3. Register:

| Field | Value |
|-------|-------|
| PyPI project name | `prism-eval` |
| Owner | `insightitsGit` |
| Repository | `prism-eval` |
| Workflow name | `release.yml` |
| Environment name | `pypi` |

4. In GitHub → **Settings → Environments → pypi** (created automatically on first run, or create manually)  
5. Push a version tag:

```bash
git tag v0.2.1
git push origin v0.2.1
```

## API token fallback

```text
GitHub repo → Settings → Secrets and variables → Actions
Name:  PYPI_API_TOKEN
Value: pypi-AgEIcHlwaS5vcmc...
```

The release job passes `password: ${{ secrets.PYPI_API_TOKEN }}` into `pypa/gh-action-pypi-publish`.

## Verify

```bash
pip index versions prism-eval
pip install prism-eval==0.2.1
python -c "import prism_eval; print(prism_eval.__version__)"
```

## Artifacts always produced (even before PyPI is linked)

On each `v*` tag:

- `dist/*.whl` + `dist/*.tar.gz`  
- `sbom.cdx.json` (CycloneDX)  
- GitHub Release attachments  
- Build provenance attestations  
