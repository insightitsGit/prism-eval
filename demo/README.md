# Prism-Eval demos

## 1) Browser interactive demo (GitHub Pages)

Open the deployed Pages site (after push to `main`), or open locally:

```bash
# from repo root
python -m http.server 8000 --directory docs
# then visit http://localhost:8000
```

Toggle **Vulnerable** vs **Hardened** agents and run the G4 suite in-browser.

## 2) Real engine (Streamlit)

```bash
pip install -e ".[demo]"
streamlit run demo/app.py
```

This runs the actual `PrismEvalEngine` against `builtin` / `ugly` / file corpora.
