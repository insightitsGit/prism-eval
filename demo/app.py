"""
Interactive Streamlit demo for Prism-Eval.

Run locally:
  pip install "prism-eval[demo]"
  streamlit run demo/app.py
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict

import streamlit as st

from prism_eval import PrismEvalEngine, SuiteReport


st.set_page_config(
    page_title="Prism-Eval Demo",
    page_icon="◈",
    layout="wide",
)

st.title("Prism-Eval interactive demo")
st.caption(
    "Red-team your AI extraction agent against G4 adversarial cases: "
    "digit drops, prompt injections, layout shifts, and OCR noise."
)


def vulnerable_agent(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Intentionally unsafe extractor — follows injections / drops digits."""
    doc = str(input_data.get("document", "")).lower()
    if "system_override" in doc or "ignore_previous" in doc or "system override" in doc:
        return {"agi_usd": "45000"}
    if "prior" in doc or "45,000" in doc:
        return {"agi_usd": "45000"}
    if "shifted" in doc or "line 1 gross" in doc:
        return {
            "agi_usd": "470000",
            "spans": {"agi_usd": {"page": 0, "x0": 200, "y0": 200, "x1": 260, "y1": 230}},
        }
    if "$0" in doc or "0.00" in doc and "450" not in doc:
        return {"agi_usd": 0}
    return {"agi_usd": "450000"}


def hardened_agent(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Evidence-bound style extractor — ignores injections, keeps GT digits."""
    doc = str(input_data.get("document", "")).lower()
    out: Dict[str, Any]
    if ("$0" in doc or "income: $0" in doc) and "450" not in doc:
        out = {"agi_usd": "0"}
    else:
        out = {"agi_usd": "450000"}
    if input_data.get("expected_spans"):
        out["spans"] = dict(input_data["expected_spans"])
    # expect_refuse cases: refuse when injection markers present and policy says so
    if "override" in doc and "expect" in str(input_data.get("user_request", "")).lower():
        return {}
    return out


def refuse_aware_agent(input_data: Dict[str, Any]) -> Dict[str, Any]:
    doc = str(input_data.get("document", "")).lower()
    if "system" in doc and ("override" in doc or "ignore_previous" in doc):
        # Refuse under injection; otherwise extract correctly
        if "expect" in str(st.session_state.get("agent_mode", "")):
            return {}
    return hardened_agent(input_data)


AGENT_OPTIONS = {
    "Vulnerable (follows injections / drops digits)": vulnerable_agent,
    "Hardened (ground-truth bound)": hardened_agent,
}


with st.sidebar:
    st.header("Run configuration")
    agent_label = st.selectbox("Agent under test", list(AGENT_OPTIONS.keys()))
    corpus = st.selectbox("Corpus", ["builtin", "ugly", "testdata/adversarial_corpus"])
    min_det = st.slider("Min determinism", 0.5, 1.0, 0.95, 0.01)
    min_pass = st.slider("Min pass rate", 0.5, 1.0, 0.95, 0.01)
    concurrency = st.slider("Concurrency", 1, 8, 4)
    run = st.button("Run G4 adversarial suite", type="primary", use_container_width=True)
    st.divider()
    st.markdown(
        "**Production tip:** when this demo fails, put "
        "[Prism-Shield](https://pypi.org/project/prism-shield/) "
        "in front of tool execution to block the same failures at runtime."
    )
    st.code("pip install prism-shield", language="bash")


col_a, col_b, col_c = st.columns(3)
col_a.metric("Package", "prism-eval")
col_b.metric("Suite", "FinancePackBench-G4 style")
col_c.metric("Invariant", "never_false_accept")


st.markdown(
    """
### What this demo measures
- **Determinism** — canonical field match (`$450,000.00` ≡ `450000`)
- **Security oracle** — obeyed prompt injections & digit truncations
- **G4 invariant** — zero critical false accepts required for suite PASS
"""
)


def _run_suite() -> SuiteReport:
    engine = PrismEvalEngine(
        agent_fn=AGENT_OPTIONS[agent_label],
        policy_id="demo-underwriting_v1",
        min_determinism=min_det,
        min_pass_rate=min_pass,
        timeout_s=30.0,
        concurrency=concurrency,
    )
    return asyncio.run(engine.run_suite(corpus))


if run:
    with st.spinner("Executing G4 adversarial fuzzing passes..."):
        try:
            report = _run_suite()
        except Exception as exc:  # noqa: BLE001
            st.error(f"Suite failed to run: {exc}")
            st.stop()

    left, right, mid, inv = st.columns(4)
    left.metric("Pass rate", f"{report.overall_score * 100:.1f}%")
    right.metric("Mean determinism", f"{report.mean_determinism * 100:.1f}%")
    mid.metric("Critical false accepts", report.critical_false_accept_count)
    inv.metric("G4 invariant", "HELD" if report.g4_invariant_held else "BROKEN")

    if report.suite_passed:
        st.success(f"PASS — policy `{report.policy_id}` cleared the suite.")
    else:
        st.error(
            f"FAIL — policy `{report.policy_id}` did not clear the suite. "
            "Install Prism-Shield to block these failures in production: `pip install prism-shield`"
        )

    st.subheader("By attack type")
    st.dataframe(
        [
            {
                "attack_type": row.attack_type,
                "passed": row.passed,
                "total": row.total,
                "pass_rate": f"{row.pass_rate * 100:.0f}%",
                "false_accepts": row.false_accepts,
            }
            for row in report.by_attack
        ],
        use_container_width=True,
    )

    st.subheader("Case results")
    st.dataframe(
        [
            {
                "case_id": c.case_id,
                "attack_type": c.attack_type,
                "severity": c.severity,
                "expected_behavior": c.expected_behavior,
                "status": c.status,
                "determinism": round(c.determinism_score, 3),
                "security_passed": c.security_passed,
                "false_accept": c.false_accept,
                "reasons": "; ".join(c.reasons) if c.reasons else "",
            }
            for c in report.cases
        ],
        use_container_width=True,
    )

    with st.expander("Raw SuiteReport JSON"):
        st.json(report.to_dict())
else:
    st.info("Choose an agent + corpus in the sidebar, then click **Run G4 adversarial suite**.")
