# Publishing `prism-eval` to PyPI

PyPI uploads are done **locally with twine** (not GitHub Actions), so the public
Release workflow stays green.

The Release workflow on tag push (`v*`) still:

- Builds sdist + wheel  
- Runs `twine check`  
- Attaches artifacts + CycloneDX SBOM to the GitHub Release  
- Attests build provenance  

## Upload with your API token

```powershell
cd c:\code\Prism_Eval
python -m build
python -m twine check dist/*

$env:TWINE_USERNAME = "__token__"
$env:TWINE_PASSWORD = "pypi-YOUR_TOKEN_HERE"   # full token including pypi- prefix
python -m twine upload dist/*
```

## Verify

```bash
pip index versions prism-eval
pip install prism-eval==0.3.1
python -c "import prism_eval; print(prism_eval.__version__)"
```

## GitHub Release artifacts

On each `v*` tag:

- `dist/*.whl` + `dist/*.tar.gz`  
- `sbom.cdx.json` (CycloneDX)  
- Build provenance attestations  
