"""Local Streamlit UI. Run from the repository root; no API/model server needed."""

from pathlib import Path
import html
import json
import sys

# Streamlit runs this file as a script; make the existing app package importable.
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from app.frontend.view import (
    BANNER, BASELINES, badge_html, citation_cell, cell_id, load_samples,
    parse_custom, plain_gap, run_lookup, table_html, value_html,
)
from scripts.tatqa_excerpt_ingestion import digest


CSS = """
<style>
.block-container {max-width:1260px;padding-top:2rem;padding-bottom:3rem;}
.source-scroll {max-height:430px;overflow:auto;border:1px solid #cbd5e1;border-radius:10px;margin:0.5rem 0 1rem;}
.source-table {border-collapse:collapse;width:100%;font-family:system-ui,sans-serif;font-size:14px;}
.source-table caption {text-align:left;padding:10px 14px;color:#475569;font-size:12px;background:#f8fafc;}
.source-table th,.source-table td {padding:12px 14px;text-align:left;border:1px solid #e2e8f0;white-space:pre-wrap;overflow-wrap:anywhere;color:#172033;background:#fff;}
.source-table tr:first-child th {background:#edf2f7;font-weight:650;}
.source-table .row-index {width:42px;color:#64748b;background:#f8fafc;font-weight:400;}
.source-table .verified-cell {background:#d1fae5;color:#064e3b;box-shadow:inset 0 0 0 2px #059669;}
.source-table .baseline-cell {background:#fef3c7;color:#78350f;box-shadow:inset 0 0 0 1px #d97706;}
.source-table :target {outline:3px solid #2563eb;outline-offset:-3px;scroll-margin-top:100px;}
.cell-refs {display:block;font-size:11px;font-weight:650;margin-top:5px;}
.decision {display:flex;align-items:center;gap:14px;border-radius:9px;padding:13px 16px;margin:0.5rem 0 1rem;font-family:system-ui,sans-serif;flex-wrap:wrap;}
.decision strong {letter-spacing:0.06em;font-size:14px;}
.decision span {font-size:14px;}
.decision.full {background:#d1fae5;color:#065f46;}
.decision.partial {background:#fef3c7;color:#78350f;}
.decision.abstain {background:#fee2e2;color:#991b1b;}
.answer-value {padding:10px 0;border-bottom:1px solid #e2e8f0;font-family:system-ui,sans-serif;overflow-wrap:anywhere;}
.answer-value strong {font-size:21px;}
.fact-label {font-size:14px;}
.answer-value a,.source-link {color:#2563eb;font-weight:650;text-decoration:underline;}
</style>
"""


def show_question(payload):
    st.subheader("Question")
    st.text(payload["question"])
    st.caption("Requested facts · explicit inputs, not automatically decomposed")
    st.dataframe([{"Requested fact": f["metric"], "Year": str(f["year"])}
                  for f in payload["requested_facts"]], hide_index=True, width="stretch")


def render_results(result, payload, prefix):
    st.subheader("Result")
    st.markdown(badge_html(result["decision"]), unsafe_allow_html=True)
    for value in result["values"]:
        st.markdown(value_html(value, result["citations"], payload["table"], prefix=prefix), unsafe_allow_html=True)
    if not result["values"]:
        st.write("No answer values are returned by the graded policy.")
    if result["citations"]:
        st.markdown("**Numbered sources**")
        for cite in result["citations"]:
            cell = citation_cell(cite, payload["table"])
            if cell:
                target = cell_id(prefix, *cell)
                raw = html.escape(payload["table"][cell[0]][cell[1]])
                st.markdown(f'<a class="source-link" target="_self" href="#{target}">[{cite["citation_number"]}] Row {cell[0]+1}, column {cell[1]+1}</a> — {raw}', unsafe_allow_html=True)
            else:
                st.write(f"[{cite['citation_number']}] Cell location unavailable; no source link inferred.")
    st.markdown("**What is missing or unresolved**")
    if result["gap_explanation"]:
        for gap in result["gap_explanation"]:
            st.text(plain_gap(gap, payload))
    else:
        st.write("All requested facts are supported by the retained evidence for this run.")
    if result["packing"]["truncated"]:
        st.warning("Only part of the source evidence fit this run. Omitted evidence could contain support or conflicts; this is not a completeness guarantee.")
    st.subheader("Three-baseline comparison")
    st.caption("Same retained evidence. E = extraction-only, B = binary, G = graded. Baseline citations link to the same source table.")
    by_name = {x["variant"]: x for x in result["baselines"]}
    for column, (variant, title, short) in zip(st.columns(3), BASELINES):
        with column:
            st.markdown(f"#### {title}")
            baseline = by_name[variant]
            st.markdown(badge_html(baseline["decision"], extraction_only=variant == "extraction_only"), unsafe_allow_html=True)
            if not baseline["values"]:
                st.write("No values returned.")
            for value in baseline["values"]:
                st.markdown(value_html(value, baseline["citations"], payload["table"], prefix=prefix, ref_prefix=short), unsafe_allow_html=True)
    st.caption("The frozen extraction-only policy reports full when it extracts any value. Binary requires full support; graded can return a supported subset. These are behavior comparisons, not scores.")


def show_source(payload, result, prefix):
    st.subheader("Source table")
    if payload.get("source_unit"):
        st.caption("Source units: " + payload["source_unit"])
    st.markdown(table_html(payload["table"], result, prefix=prefix), unsafe_allow_html=True)
    if result:
        st.caption("Green: support for the returned graded answer. Amber: baseline citation, not verified support. Click a numbered citation to focus its cell (blue outline).")
    else:
        st.caption("Run the case to highlight cited cells.")


def run_and_store(payload, key):
    st.session_state.pop(key, None)
    try:
        with st.spinner("Checking the supplied table…"):
            result = run_lookup(payload)
        st.session_state[key] = {"signature": digest(payload), "result": result}
    except (ValueError, OSError, RuntimeError) as exc:
        st.error("Could not run this input: " + str(exc) + ". Header repair is unsupported.")


def main():
    st.set_page_config(page_title="RAGSmith · Evidence prototype", page_icon="📄", layout="wide",
                       menu_items={"Get Help": None, "Report a bug": None})
    st.markdown(CSS, unsafe_allow_html=True)
    st.title("RAGSmith · Evidence prototype")
    st.warning(BANNER)
    st.caption("Runs locally through the existing pipeline · Local model OFF · No external inference API")
    prepared, custom, limitations = st.tabs(["Prepared pilot cases", "Paste your own table", "Limitations"])
    with prepared:
        try:
            packet = load_samples()
        except (OSError, ValueError, KeyError) as exc:
            st.error("The six local pilot samples are unavailable. Run `.venv-api\\Scripts\\python.exe -m app.prepare_samples` from the repository root. No data is downloaded.")
            packet = None
        if packet:
            cases = packet["cases"]
            labels = {"full": "Full", "partial": "Partial", "controlled_conflict": "Conflict · controlled test case", "abstain": "Abstain"}
            options = {f"{case['sample_id']} · {labels[case['demo_category']]}": case for case in cases}
            choice = st.selectbox("Choose a prepared case", list(options), key="pilot_case")
            case = options[choice]
            payload = case["request"]
            if case["demo_category"] == "controlled_conflict":
                st.info("Controlled test case. This reuses the pilot's artificial conflicting value; it is not a genuine report disagreement.")
            show_question(payload)
            if st.button("Run", type="primary", key="run_pilot"):
                run_and_store(payload, "pilot_result")
            stored = st.session_state.get("pilot_result", {})
            result = stored.get("result") if stored.get("signature") == digest(payload) else None
            show_source(payload, result, "pilot")
            if result:
                render_results(result, payload, "pilot")
    with custom:
        st.subheader("Try an ad hoc table")
        st.caption("This is a local prototype input, not evaluation/development data. Supply facts explicitly. Header repair is unsupported.")
        question = st.text_area("Question", "Give synthetic Revenue and Cash in 2025.", key="custom_question")
        facts = st.text_area("Requested facts (JSON)", json.dumps([
            {"requirement_id": "revenue", "metric": "Revenue", "year": 2025},
            {"requirement_id": "cash", "metric": "Cash", "year": 2025}], indent=2), height=210, key="custom_facts")
        table = st.text_area("Source table (JSON rows)", json.dumps([
            ["Metric", "2025"], ["Revenue", "10"], ["Cash", "4"]], indent=2), height=210, key="custom_table")
        unit = st.text_input("Source units (optional)", "USD millions", key="custom_unit")
        if st.button("Run pasted table", type="primary", key="run_custom"):
            st.session_state.pop("custom_result", None)
            try:
                payload = parse_custom(question, facts, table, unit)
                run_and_store(payload, "custom_result")
            except ValueError as exc:
                st.error(str(exc))
        stored = st.session_state.get("custom_result", {})
        # Changing any input hides stale decisions/cell links until the next run.
        try:
            payload = parse_custom(question, facts, table, unit)
        except ValueError:
            payload = None
        result = stored.get("result") if payload and stored.get("signature") == digest(payload) else None
        if result:
            show_source(payload, result, "custom")
            render_results(result, payload, "custom")
    with limitations:
        st.markdown(Path(__file__).with_name("limitations.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
